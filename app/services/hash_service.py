# from passlib.context import CryptContext


# class HashService:
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#     @classmethod
#     def hash_password(cls, password: str) -> str:
#         return cls.pwd_context.hash(password)

#     @classmethod
#     def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
#         return cls.pwd_context.verify(plain_password, hashed_password)


from passlib.hash import pbkdf2_sha256

class HashService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pbkdf2_sha256.verify(password, hashed)
