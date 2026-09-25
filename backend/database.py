"""
HireScope Backend — database.py
In-memory storage for users and interview sessions.
"""

from typing import Dict, Any
import hashlib

# ── Storage ───────────────────────────────────────────

# { email: { name, email, password } }
users_db: Dict[str, Dict[str, Any]] = {}

# { session_id: { ... full session state ... } }
sessions_db: Dict[str, Dict[str, Any]] = {}


# ── Utils ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using SHA256 (basic security for demo)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ── User Functions ────────────────────────────────────

def get_user(email: str) -> Dict[str, Any] | None:
    return users_db.get(email)


def create_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user (prevents duplicates)."""
    if email in users_db:
        raise ValueError("User already exists")

    user = {
        "name": name,
        "email": email,
        "password": hash_password(password),   # 🔥 FIXED
    }

    users_db[email] = user
    return user


# ── Session Functions ─────────────────────────────────

def get_session(session_id: str) -> Dict[str, Any]:
    """Get session or raise error if not found."""
    session = sessions_db.get(session_id)
    if not session:
        raise ValueError("Session not found")   # 🔥 FIXED
    return session


def set_session(session_id: str, data: Dict[str, Any]) -> None:
    """Store/update session data."""
    sessions_db[session_id] = data