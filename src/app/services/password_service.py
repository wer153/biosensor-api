import bcrypt


class PasswordService:
    """Simple password hashing service using bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with salt rounds=12"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# TODO: Add password validation policy
# - Minimum 8 characters
# - At least one uppercase, lowercase, number, special character
# - No common passwords
# - No repeated characters
password_service = PasswordService()
