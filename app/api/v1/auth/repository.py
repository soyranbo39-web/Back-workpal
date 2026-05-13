from uuid import uuid4

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password, verify_password
from app.models.Users import UserORM


class AuthRepository:
	def get_by_username(self, username: str) -> UserORM | None:
		with SessionLocal() as db:
			return db.execute(
				select(UserORM).where(UserORM.username == username)
			).scalars().first()

	def create_user(self, username: str, password: str) -> UserORM:
		with SessionLocal() as db:
			user = UserORM(
				id=str(uuid4()),
				username=username,
				password_hash=hash_password(password),
			)
			db.add(user)
			db.commit()
			db.refresh(user)
			return user

	def authenticate(self, username: str, password: str) -> UserORM | None:
		user = self.get_by_username(username)
		if user is None:
			return None
		if not verify_password(password, user.password_hash):
			return None
		return user

	def get_by_id(self, user_id: str) -> UserORM | None:
		with SessionLocal() as db:
			return db.get(UserORM, user_id)
