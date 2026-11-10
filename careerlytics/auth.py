from __future__ import annotations

import hashlib
import hmac
import os
import re

ITERATIONS = 200_000
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS).hex()
    return digest, salt

def verify_password(password: str, digest: str, salt: str) -> bool:
    return hmac.compare_digest(hash_password(password, salt)[0], digest)

def validate_signup(username: str, email: str, password: str, confirm: str) -> str | None:
    if len(username.strip()) < 2:
        return "Please enter a username (at least 2 characters)."
    if not EMAIL_RE.match(email.strip()):
        return "Please enter a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if password != confirm:
        return "Passwords do not match."
    return None

def sign_up(db, username: str, email: str, password: str, confirm: str):
    """Returns (user_dict, error). user_dict = {id, username, email}."""
    err = validate_signup(username, email, password, confirm)
    if err:
        return None, err
    h, salt = hash_password(password)
    try:
        uid = db.create_user(username, email, h, salt)
    except ValueError as e:
        return None, str(e)
    return {"id": uid, "username": username.strip(), "email": email.strip().lower()}, None

def log_in(db, email: str, password: str):
    row = db.get_user_by_email(email) if email.strip() else None
    if not row or not verify_password(password, row["password_hash"], row["salt"]):
        return None, "Incorrect email or password."
    return {"id": int(row["user_id"]), "username": row["username"], "email": row["email"]}, None
