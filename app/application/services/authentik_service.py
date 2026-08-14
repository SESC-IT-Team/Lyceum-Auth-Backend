from uuid import UUID
import json

from sesc_auth_sdk.services.requests_service import RequestsService
from sqlalchemy.dialects.postgresql import Any

from app.domain.entities.authentik_user import AuthentikUser
import logging

logger = logging.getLogger(__name__)

class AuthentikService:
    def _make_user_authentik_payload(self, username: str | None, name: str | None) -> dict[str, Any]:
        res = {"is_active": True, "path": self._users_path}
        if username:
            res["username"] = username
        if name:
            res["name"] = name
        return res

    async def _make_request(self, uri: str, method: str, expected_status: int = 200, **kwargs):
        kwargs.update({'headers': {'Content-Type': 'application/json'}})
        return await RequestsService.authorized_request(self._authentik_url + uri, self._api_token, method, expected_status=expected_status, **kwargs)

    def __init__(self, authentik_url: str, users_path: str, api_token: str):
        self._authentik_url = authentik_url
        self._api_token = api_token
        self._users_path = users_path

    async def get_user_by_login(self, login: str) -> AuthentikUser | None:
        res = await self._make_request(f'/api/v3/core/users/?search={login}', "GET", expected_status=200)
        res = res['results']
        result = {}
        for user in res:
            if user['username'] == login:
                result = user
                break
        if result == {}:
            return None
        return AuthentikUser(**result)

    async def create_user(self, username: str, name: str) -> tuple[int, UUID]:
        try:
            res = await self._make_request('/api/v3/core/users/', "POST", expected_status=201, data=json.dumps(self._make_user_authentik_payload(username, name)))
            logger.info('User creation successful')
        except Exception as e:
            logger.error(f'User creation failed, username={username}, name={name}, error={e}')
            raise
        return res["pk"], UUID(res['uuid'])

    async def update_user_info(self, pk: int, username: str | None, name: str | None):
        if username or name:
            try:
                await self._make_request(f'/api/v3/core/users/{pk}/', "PATCH",
                                         expected_status=200,
                                         data=json.dumps(self._make_user_authentik_payload(username, name)))
                logger.info(f'User info update successful, pk={pk}' + f' username={username}' if username else '' + f' name={name}' if name else '')
            except Exception as e:
                logger.error(f'User info update failed, pk={pk} error={e}' + f' username={username}' if username else '' + f' name={name}' if name else '')
                raise

    async def update_user_password(self, pk: int, password: str):
        try:
            await self._make_request(f'/api/v3/core/users/{pk}/set_password/', "POST",
                                                  data=json.dumps({'password': password}),
                                                  expected_status=204)

            logger.info(f'Password update successful, pk={pk}')
        except Exception as e:
            logger.error(f'Password update failed, pk={pk} error={e}')
            raise

    async def delete_user(self, pk: int):
        try:
            await self._make_request(f'/api/v3/core/users/{pk}/', "DELETE",
                                                  expected_status=204)
            logger.error(f'User deletion successful, pk={pk}')
        except Exception as e:
            logger.error(f'User deletion failed, pk={pk} error={e}')
            raise
