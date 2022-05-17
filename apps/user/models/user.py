from pydantic import BaseModel


class User(BaseModel):
    email: str
    display_name: str
    gauss_refresh_token: str
