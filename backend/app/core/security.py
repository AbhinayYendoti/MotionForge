import base64
from dataclasses import dataclass

import jwt
from jwt import PyJWKClient

from app.core.config import settings


@dataclass(frozen=True)
class AuthUser:
    clerk_id: str
    email: str


def _issuer_from_publishable_key() -> str | None:
    if settings.clerk_jwt_issuer:
        return settings.clerk_jwt_issuer.rstrip("/")
    prefixes = ("pk_test_", "pk_live_")
    raw = settings.clerk_publishable_key
    for prefix in prefixes:
        if raw.startswith(prefix):
            encoded = raw.removeprefix(prefix)
            padding = "=" * (-len(encoded) % 4)
            host = base64.urlsafe_b64decode((encoded + padding).encode()).decode().strip("$")
            return f"https://{host}".rstrip("/")
    return None


def verify_clerk_token(token: str, fallback_email: str | None = None) -> AuthUser:
    if settings.auth_bypass:
        return AuthUser(clerk_id=token or "local-dev-user", email=fallback_email or "local@motionforge.dev")

    issuer = _issuer_from_publishable_key()
    if not issuer:
        raise ValueError("CLERK_JWT_ISSUER is required when the Clerk publishable key issuer cannot be derived.")

    jwks_client = PyJWKClient(f"{issuer}/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=issuer,
        options={"verify_aud": False},
    )
    clerk_id = payload.get("sub")
    if not clerk_id:
        raise ValueError("Clerk token is missing a subject.")
    email = payload.get("email") or fallback_email or f"{clerk_id}@clerk.local"
    return AuthUser(clerk_id=clerk_id, email=email)

