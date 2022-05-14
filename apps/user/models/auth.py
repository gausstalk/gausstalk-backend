from pydantic import BaseModel


class Auth(BaseModel):
    code: str
    session_state: str
