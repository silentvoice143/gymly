from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.auth_controller import AuthController

auth_ns = Namespace("Auth", description="Authentication APIs")

# Swagger request models
signup_model = auth_ns.model("SignupModel", {
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

login_model = auth_ns.model("LoginModel", {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})


@auth_ns.route("/signup")
class SignupAPI(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, "User created")
    @auth_ns.response(400, "Validation error")
    def post(self):
        data = request.get_json()
        user, error = AuthController.signup(data)

        if error:
            return {"error": error}, 400

        return {"message": "User created successfully"}, 201


@auth_ns.route("/login")
class LoginAPI(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, "Login successful")
    @auth_ns.response(401, "Invalid credentials")
    def post(self):
        data = request.get_json()
        response, error = AuthController.login(data)

        if error:
            return {"error": error}, 401

        return response, 200
