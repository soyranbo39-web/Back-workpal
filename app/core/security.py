import hmac
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

from app.core.config import (
	API_KEY_HEADER_NAME,
	API_KEY_VALUE,
	AUTH_COOKIE_NAME,
	AUTH_JWT_ALGORITHM,
	AUTH_SECRET_KEY,
	AUTH_TOKEN_EXPIRE_MINUTES,
)

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_revoked_jtis: set[str] = set()


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
	return pwd_context.verify(password, password_hash)


def create_access_token(user_id: str, permissions: list[str] | None = None) -> str:
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=AUTH_TOKEN_EXPIRE_MINUTES)
	payload = {
		"sub": user_id,
		"exp": expires_at,
		"perms": permissions or [],
		"jti": str(uuid.uuid4()),
	}
	return jwt.encode(payload, AUTH_SECRET_KEY, algorithm=AUTH_JWT_ALGORITHM)


def revoke_token(token: str) -> None:

	try:
		payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_JWT_ALGORITHM])
		jti = payload.get("jti")
		if jti:
			_revoked_jtis.add(jti)
	except jwt.JWTError:
		pass  


def decode_access_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_JWT_ALGORITHM])
	except jwt.ExpiredSignatureError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado") from exc
	except jwt.JWTError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido") from exc
	return payload


def require_authenticated_user(
	request: Request,
	token: str | None = Depends(oauth2_scheme),
) -> str:
	if token is None:
		token = request.cookies.get(AUTH_COOKIE_NAME)
	if token is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

	payload = decode_access_token(token)
	user_id = payload.get("sub")
	permissions = payload.get("perms", [])
	jti = payload.get("jti")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
	if jti and jti in _revoked_jtis:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion cerrada, inicia sesion nuevamente")
	if "access_protected_endpoints" not in permissions:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
	return str(user_id)


def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
	if api_key is None or not hmac.compare_digest(api_key, API_KEY_VALUE):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="API key invalida o ausente",
		)
	return api_key


def get_current_user(
	request: Request,
	token: str | None = Depends(oauth2_scheme),
) -> str:

	return require_authenticated_user(request=request, token=token)
