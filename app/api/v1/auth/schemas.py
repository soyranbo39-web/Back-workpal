from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
	username: str = Field(min_length=3, max_length=60)
	password: str = Field(min_length=6, max_length=100)


class LoginIn(BaseModel):
	username: str
	password: str


class CookieMetaOut(BaseModel):
	name: str
	http_only: bool
	secure: bool
	same_site: str
	max_age_seconds: int


class AuthOut(BaseModel):
	access_token: str
	token_type: str = "bearer"
	cookie: CookieMetaOut


class UserOut(BaseModel):
	id: str
	username: str


class SessionOut(BaseModel):
	user_id: str
	authenticated: bool
	authenticated_via_cookie: bool
	cookie_name: str
