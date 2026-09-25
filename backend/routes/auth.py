"""
HireScope Backend — routes/auth.py
"""

from fastapi import APIRouter
from pydantic import BaseModel
import hashlib

from backend.database import get_user, create_user

router = APIRouter()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token(email: str) -> str:
    import time
    raw = f"{email}:{time.time()}"
    return "hs_" + hashlib.md5(raw.encode()).hexdigest()


@router.post("/signup")
def signup(body: SignupRequest):
    if get_user(body.email):
        return {"success": False, "error": "User already exists"}

    user  = create_user(body.name.strip(), body.email.strip().lower(), body.password)
    token = _generate_token(body.email)

    return {
        "success": True,
        "token": token,
        "user": {"name": user["name"], "email": user["email"]},
    }


@router.post("/login")
def login(body: LoginRequest):
    user = get_user(body.email.strip().lower())

    if not user:
        return {"success": False, "error": "User not found"}

    if user["password"] != _hash_password(body.password):
        return {"success": False, "error": "Incorrect password"}

    token = _generate_token(body.email)

    return {
        "success": True,
        "token": token,
        "user": {"name": user["name"], "email": user["email"]},
    }