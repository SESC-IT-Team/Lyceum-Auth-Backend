from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.permission import PermissionType
from app.domain.enums.role import Role


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    user_id: UUID
    roles: list[Role]
    permissions: list[PermissionType]

class Jwk(BaseModel):
    kty: str  # тип ключа (RSA)
    kid: str  # key id
    use: str  # обычно "sig"
    alg: str  # алгоритм (RS256)
    n: str    # modulus (base64url)
    e: str    # exponent (base64url)


class JwksResponse(BaseModel):
    keys: list[Jwk]