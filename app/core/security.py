from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Security:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not hashed_password:
            return False
        
        # Kiểm tra xem chuỗi trong DB có phải là Bcrypt hay không (thường bắt đầu bằng $2b$)
        is_bcrypt = hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$")
        
        if is_bcrypt:
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                return False
        else:
            # Nếu chưa mã hóa, so sánh trực tiếp văn bản thuần
            return plain_password == hashed_password

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
