from pydantic import BaseModel

from app.domain.enums.department import Department
from app.domain.enums.position import Position


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    user_id: str
    role: str
    permissions: list[str]
    departments: list[Department] | None
    position: Position | None

class Jwk(BaseModel):
    kty: str  # тип ключа (RSA)
    kid: str  # key id
    use: str  # обычно "sig"
    alg: str  # алгоритм (RS256)
    n: str    # modulus (base64url)
    e: str    # exponent (base64url)


class JwksResponse(BaseModel):
    keys: list[Jwk]