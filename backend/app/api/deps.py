from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import AuthUser, verify_clerk_token
from app.database.session import get_db
from app.repositories.projects import upsert_user


def get_auth_user(
    authorization: Annotated[str | None, Header()] = None,
    x_clerk_email: Annotated[str | None, Header()] = None,
) -> AuthUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        return verify_clerk_token(token, fallback_email=x_clerk_email)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


def get_current_db_user(
    auth_user: Annotated[AuthUser, Depends(get_auth_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user = upsert_user(db, auth_user.clerk_id, auth_user.email)
    db.commit()
    db.refresh(user)
    return user

