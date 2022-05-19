from pydantic import BaseModel


class Auth(BaseModel):
    code: str
    session_state: str


class AccessToken(BaseModel):
    gauss_access_token: str | None
