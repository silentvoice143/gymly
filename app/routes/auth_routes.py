from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.auth_controller import AuthController

auth_ns = Namespace("Auth", description="Authentication APIs")

# Swagger request models
signup_model = auth_ns.model("SignupModel", {
    "name": fields.String(required=True, description="User full name"),
    "email": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, description="Password")
})

signup_gym_owner_model = auth_ns.model("SignupGymOwnerModel", {
    "name": fields.String(required=True, description="Gym owner full name"),
    "email": fields.String(required=True, description="Gym owner email"),
    "password": fields.String(required=True, description="Password")
})

login_model = auth_ns.model("LoginModel", {
    "email": fields.String(required=True, description="Email address"),
    "password": fields.String(required=True, description="User password")
})

# ----------------------------------------------------------
# SIGNUP (Regular User)
# ----------------------------------------------------------
@auth_ns.route("/signup")
class SignupAPI(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, "User created successfully")
    @auth_ns.response(400, "Validation error")
    def post(self):
        data = request.get_json()
        user, error = AuthController.signup(data)

        if error:
            return {"error": error}, 400

        return {"message": "User created successfully"}, 201


# ----------------------------------------------------------
# SIGNUP (Gym Owner)
# ----------------------------------------------------------
@auth_ns.route("/signup-gym-owner")
class SignupGymOwnerAPI(Resource):
    @auth_ns.expect(signup_gym_owner_model)
    @auth_ns.response(201, "Gym owner created successfully")
    @auth_ns.response(400, "Validation error")
    def post(self):
        data = request.get_json()
        user, error = AuthController.signup_gym_owner(data)

        if error:
            return {"error": error}, 400

        return {"message": "Gym owner created successfully"}, 201


# ----------------------------------------------------------
# LOGIN
# ----------------------------------------------------------
@auth_ns.route("/login")
class LoginAPI(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, "Login successful")
    @auth_ns.response(401, "Invalid email or password")
    def post(self):
        data = request.get_json()
        response, error = AuthController.login(data)

        if error:
            return {"error": error}, 401

        return response, 200
