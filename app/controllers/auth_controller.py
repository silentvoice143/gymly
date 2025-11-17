from app.services.auth_service import AuthService

class AuthController:

    @staticmethod
    def signup(data):
        user, error = AuthService.signup(
            name=data["name"],
            email=data["email"],
            password=data["password"]
        )
        return user, error

    @staticmethod
    def login(data):
        response, error = AuthService.login(
            email=data["email"],
            password=data["password"]
        )
        return response, error
