from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import (
	AUTH_COOKIE_NAME,
	AUTH_COOKIE_SECURE,
	AUTH_TOKEN_EXPIRE_MINUTES,
)
from app.core.security import (
	create_access_token,
	require_authenticated_user,
	
	
)
from app.api.v1.auth.repository import AuthRepository
from app.api.v1.auth.schemas import (
	AuthOut,
	CookieMetaOut,
	RegisterIn,
	SessionOut,
	UserOut,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])
repo = AuthRepository()


@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn):
	exists = repo.get_by_username(body.username)
	if exists is not None:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ya existe")

	user = repo.create_user(body.username, body.password)
	return UserOut(id=user.id, username=user.username)

@auth_router.post("/token", response_model=AuthOut)
def login(response: Response, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
	user = repo.authenticate(form.username, form.password)
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

	token = create_access_token(user.id, permissions=["access_protected_endpoints"])
	response.set_cookie(
		key=AUTH_COOKIE_NAME,
		value=token,
		httponly=True,
		secure=AUTH_COOKIE_SECURE,
		samesite="lax",
		max_age=AUTH_TOKEN_EXPIRE_MINUTES * 60,
	)
	return AuthOut(
		access_token=token,
		cookie=CookieMetaOut(
			name=AUTH_COOKIE_NAME,
			http_only=True,
			secure=AUTH_COOKIE_SECURE,
			same_site="lax",
			max_age_seconds=AUTH_TOKEN_EXPIRE_MINUTES * 60,
		),
	)


@auth_router.get("/me", response_model=UserOut)
def me(user_id: Annotated[str, Depends(require_authenticated_user)]):
	user = repo.get_by_id(user_id)
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
	return UserOut(id=user.id, username=user.username)


@auth_router.get("/session", response_model=SessionOut)
def session_info(
	request: Request,
	user_id: Annotated[str, Depends(require_authenticated_user)],
):
	return SessionOut(
		user_id=user_id,
		authenticated=True,
		authenticated_via_cookie=AUTH_COOKIE_NAME in request.cookies,
		cookie_name=AUTH_COOKIE_NAME,
	)

