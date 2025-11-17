# 💪 Gymly

> Smart Gym Attendance & Booking Platform

A modern Flask-based platform for managing gym memberships, bookings, and attendance tracking.

---

## 🔥 Day 1 - Project Setup

### ✅ What We Built

- ✔ Created project folder: `gymly_backend/`
- ✔ Built app factory pattern with `create_app()`
- ✔ Set up configuration and extensions
- ✔ Created virtual environment
- ✔ Installed all dependencies
- ✔ Added `run.py` to start the server
- ✔ Successfully tested the development server

### 📁 Project Structure

```
gymly_backend/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Settings
│   ├── extensions.py        # DB + Migrations
│   └── models/              # Database models folder
├── venv/                    # Virtual environment
└── run.py                   # Start server
```

### 🚀 Commands Used

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-sqlalchemy flask-migrate psycopg2-binary

# Run the server
python run.py
```

---

## 🔥 Day 2 - Database Models & Relationships

### ✅ What We Built

- ✔ Created all database models using OOP
- ✔ Added relationships (one-to-many, many-to-one)
- ✔ Implemented password hashing methods
- ✔ Added trial period calculation
- ✔ Updated `models/__init__.py` with imports
- ✔ Initialized Flask-Migrate
- ✔ Created and applied first migration

### 🗄️ Database Models

#### 👤 User (`user.py`)

```python
- id, name, email, password_hash, role
- Methods: set_password(), check_password()
- Relations: gyms, bookings, attendance_records
```

#### 🏋️ Gym (`gym.py`)

```python
- id, name, location, owner_id
- Relations: owner, bookings, attendance_records
```

#### 📅 Subscription (`subscription.py`)

```python
- id, user_id, start_date, end_date, plan
- Static Method: trial_period() → 60 days
```

#### 🎫 Booking (`booking.py`)

```python
- id, user_id, gym_id, booking_date, status, amount
- Relations: user, gym
```

#### ✅ Attendance (`attendance.py`)

```python
- id, user_id, gym_id, timestamp
- Relations: user, gym
```

### 🔗 How to Create Model Relationships

**Complete Relationship Setup (2 Steps)**

#### Step 1: Add Foreign Key (Child Model)

```python
# In Booking model (child)
gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"))
```

#### Step 2: Add relationship() (Both Models)

```python
# In Booking model (child)
gym = db.relationship("Gym", back_populates="bookings")

# In Gym model (parent)
bookings = db.relationship("Booking", back_populates="gym")
```

**📌 Important Rules:**

- ✅ Foreign Key goes in the **child** model (the "many" side)
- ✅ `relationship()` goes in **both** models
- ✅ `back_populates` must match the variable name in the other model
- ✅ Foreign Key uses table name: `"gyms.id"`
- ✅ relationship() uses class name: `"Gym"`

---

### 📚 All Relationship Types Explained

#### 1️⃣ One-to-Many (Most Common)

**Example:** One User has Many Bookings

```python
# Parent Model (User - ONE side)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

    # Relationship (returns LIST)
    bookings = db.relationship("Booking", back_populates="user")

# Child Model (Booking - MANY side)
class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key (required!)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Relationship (returns SINGLE object)
    user = db.relationship("User", back_populates="bookings")
```

**Usage:**

```python
user = User.query.get(1)
user.bookings  # [<Booking 1>, <Booking 2>, ...]

booking = Booking.query.get(1)
booking.user  # <User 1>
```

---

#### 2️⃣ One-to-One

**Example:** One User has One Profile

```python
# Parent Model (User)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

    # uselist=False makes it One-to-One
    profile = db.relationship("Profile", back_populates="user", uselist=False)

# Child Model (Profile)
class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text)

    # Foreign Key + unique=True ensures one-to-one
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    user = db.relationship("User", back_populates="profile")
```

**Key Differences:**

- ✅ Add `uselist=False` in parent model
- ✅ Add `unique=True` to foreign key
- ✅ Returns single object, not list

**Usage:**

```python
user = User.query.get(1)
user.profile  # <Profile 1> (single object, not list)
```

---

#### 3️⃣ Many-to-Many

**Example:** Users can join Multiple Gyms, Gyms have Multiple Members

```python
# Association Table (junction table)
gym_members = db.Table('gym_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('gym_id', db.Integer, db.ForeignKey('gyms.id'))
)

# First Model (User)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

    # secondary points to association table
    memberships = db.relationship("Gym", secondary=gym_members, back_populates="members")

# Second Model (Gym)
class Gym(db.Model):
    __tablename__ = "gyms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    members = db.relationship("User", secondary=gym_members, back_populates="memberships")
```

**Key Points:**

- ✅ Need separate association table
- ✅ No foreign keys in main models
- ✅ Use `secondary=` parameter
- ✅ Both sides return lists

**Usage:**

```python
user = User.query.get(1)
user.memberships  # [<Gym 1>, <Gym 2>, ...]

gym = Gym.query.get(1)
gym.members  # [<User 1>, <User 2>, ...]
```

---

#### 4️⃣ Self-Referential (Advanced)

**Example:** User can follow other Users

```python
# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

    # Following relationship
    following = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers"
    )

    # Followers relationship
    followers = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following"
    )
```

**Usage:**

```python
user = User.query.get(1)
user.following  # Users this user follows
user.followers  # Users following this user
```

---

### 📊 Quick Reference Table

| Relationship     | Foreign Key | unique=True | uselist=False | secondary= |
| ---------------- | ----------- | ----------- | ------------- | ---------- |
| One-to-Many      | ✅ (child)  | ❌          | ❌            | ❌         |
| One-to-One       | ✅ (child)  | ✅          | ✅ (parent)   | ❌         |
| Many-to-Many     | ❌          | ❌          | ❌            | ✅         |
| Self-Referential | ❌          | ❌          | ❌            | ✅         |

---

### 💡 Gymly Project Uses

In our project we use:

- **One-to-Many**: User → Gyms, User → Bookings, Gym → Bookings
- **One-to-One**: User → Subscription (could be implemented)
- **Many-to-Many**: Not used yet (but could add for gym memberships)

### 📊 Relationship Map

```
User ──(owns)──→ Gym
User ──(books)──→ Booking ──→ Gym
User ──(attends)──→ Attendance ──→ Gym
User ──(has)──→ Subscription
```

### 🧪 Migration Commands

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial tables"

# Apply to database
flask db upgrade
```

---

## 🔥 Day 3 - OOP Architecture & JWT Authentication

### ✅ What We Built

- ✔ Restructured project with enterprise-grade architecture
- ✔ Created Routes → Controller → Service → Model flow
- ✔ Implemented JWT token-based authentication
- ✔ Added password hashing with PBKDF2-SHA256
- ✔ Built middleware for token & role verification
- ✔ Set up Flask-RESTX with Swagger documentation
- ✔ Created signup and login endpoints

### 📁 New Project Structure

```
app/
├── config/
│   └── settings.py          # Configuration
│
├── extensions/
│   ├── db.py               # Database
│   ├── migrate.py          # Migrations
│   ├── ma.py               # Marshmallow
│   └── api.py              # Flask-RESTX
│
├── models/                  # Database models
│   ├── user.py
│   ├── gym.py
│   ├── booking.py
│   └── attendance.py
│
├── routes/                  # API endpoints
│   └── auth_routes.py
│
├── controllers/             # Request handlers
│   └── auth_controller.py
│
├── services/                # Business logic
│   └── auth_service.py
│
├── middleware/              # Security layer
│   ├── token_middleware.py
│   └── role_middleware.py
│
└── utils/                   # Helper functions
    └── password.py
```

---

### 🏗️ Architecture Explained

**Request Flow:**

```
HTTP Request → Route (RESTX) → Controller → Service → Model → Database
                  ↑
              Middleware
```

#### Layer Responsibilities:

**🔹 Routes (Flask-RESTX)**

- Define API endpoints (`/auth/signup`)
- Handle HTTP methods (GET, POST, PUT, DELETE)
- Validate request data
- Apply middleware decorators

```python
@auth_ns.route("/signup")
class SignupAPI(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        return AuthController.signup(request.json)
```

**🔹 Controllers**

- Coordinate between routes and services
- Handle request/response formatting
- Call appropriate service methods

```python
class AuthController:
    @staticmethod
    def signup(data):
        return AuthService.signup(data)
```

**🔹 Services**

- Business logic implementation
- Database operations
- Data validation
- Token generation

```python
class AuthService:
    @staticmethod
    def signup(email, password):
        # Hash password
        # Create user
        # Generate JWT
        return token, user
```

**🔹 Middleware**

- Authentication verification
- Role-based access control
- Token validation

```python
@token_required
@require_role("admin")
def admin_only_route():
    pass
```

**How Token Middleware Works:**

```python
from flask import request, jsonify
import jwt
from app.config.settings import Config
from app.models.user import User

def token_required(fn):
    """
    Decorator that protects routes by requiring valid JWT token

    How it works:
    1. Extracts token from Authorization header
    2. Validates token format (Bearer <token>)
    3. Decodes JWT and verifies signature
    4. Fetches user from database
    5. Passes user object to protected route
    """
    def wrapper(*args, **kwargs):
        # Step 1: Get Authorization header
        auth_header = request.headers.get("Authorization")
        # Example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Step 2: Validate header format
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization required"}), 401

        # Step 3: Extract token (remove "Bearer " prefix)
        token = auth_header.split(" ")[1]
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        try:
            # Step 4: Decode and verify JWT
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            # data = {"user_id": 1, "role": "user", "exp": 1732818120}

            # Step 5: Fetch user from database
            user = User.query.get(data["user_id"])

        except Exception:
            # Token expired, invalid signature, or malformed
            return jsonify({"error": "Invalid or expired token"}), 401

        # Step 6: Call the protected function with user object
        return fn(user, *args, **kwargs)

    # Preserve original function name for Flask routing
    wrapper.__name__ = fn.__name__
    return wrapper
```

**Usage Example:**

```python
@app.route("/profile")
@token_required
def get_profile(user):
    # 'user' is automatically passed by middleware
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })
```

**Key Points:**

- ✅ **Automatic Authentication** - No manual token checking needed
- ✅ **User Injection** - Protected routes automatically receive user object
- ✅ **Security** - Validates token signature and expiration
- ✅ **Error Handling** - Returns 401 for invalid/missing tokens
- ✅ **Reusable** - Apply to any route that needs authentication

**Common Errors Caught:**

- Missing Authorization header
- Wrong format (not "Bearer <token>")
- Expired token
- Invalid signature
- Tampered token
- User deleted from database

**🔹 Models**

- Database table definitions
- Relationships
- Model methods

---

### 🔐 JWT Authentication

**Why JWT?**

- ✅ Stateless (no server-side sessions)
- ✅ Works with mobile & web apps
- ✅ Secure token-based auth
- ✅ Contains user info + expiration

**JWT Payload:**

```json
{
  "user_id": 1,
  "role": "user",
  "exp": 1732818120
}
```

**How It Works:**

1. User logs in with email/password
2. Server verifies credentials
3. Server generates JWT token
4. Client stores token
5. Client sends token with each request
6. Server verifies token

**Implementation:**

```python
import jwt
from datetime import datetime, timedelta

# Generate token
token = jwt.encode({
    'user_id': user.id,
    'role': user.role,
    'exp': datetime.utcnow() + timedelta(hours=24)
}, SECRET_KEY)

# Verify token
payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

---

### 🔒 Password Security (PBKDF2-SHA256)

**Why PBKDF2-SHA256?**

- ✅ Industry standard (used by Django, Dropbox)
- ✅ Slow hashing (protects against brute-force)
- ✅ Salted automatically
- ✅ Configurable iterations

**Implementation:**

```python
from passlib.hash import pbkdf2_sha256

class PasswordHasher:
    @staticmethod
    def hash(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify(password, hashed):
        return pbkdf2_sha256.verify(password, hashed)
```

**Never store plain passwords!**

---

### 👥 Role-Based Access Control

**Three Roles:**

- **User** - Regular gym members
- **Owner** - Gym owners (can manage their gyms)
- **Admin** - Platform administrators

**Model Implementation:**

```python
class User(db.Model):
    role = db.Column(db.String(50), default="user")
```

**Middleware Protection:**

```python
@require_role("admin")
def admin_dashboard():
    # Only admins can access
    pass

@require_role(["owner", "admin"])
def manage_gym():
    # Owners and admins can access
    pass
```

---

### 📝 Signup Flow (Step-by-Step)

```
1. POST /auth/signup
   ↓
2. Route validates JSON data
   ↓
3. Controller receives data
   ↓
4. Service hashes password
   ↓
5. Service creates User model
   ↓
6. Database saves user
   ↓
7. Service generates JWT token
   ↓
8. Response: { "token": "...", "user": {...} }
```

---

### 🔑 Login Flow (Step-by-Step)

```
1. POST /auth/login
   ↓
2. Service finds user by email
   ↓
3. Service verifies password hash
   ↓
4. Service generates JWT token
   ↓
5. Response: { "token": "...", "user": {...} }
```

---

### 📚 Swagger Documentation

**Access at:** `http://localhost:5000/docs`

**Features:**

- ✅ Interactive API testing
- ✅ Auto-generated from code
- ✅ Request/response examples
- ✅ Organized by namespaces

**Setup:**

```python
from flask_restx import Api

api = Api(
    title='Gymly API',
    version='1.0',
    description='Smart Gym Management Platform',
    doc='/docs'
)
```

---

### 🛠️ Key Dependencies

```bash
# Authentication & Security
pip install flask-jwt-extended
pip install passlib

# API Documentation
pip install flask-restx

# Serialization
pip install marshmallow
pip install flask-marshmallow
```

---

### 🧪 Testing Authentication

**Signup:**

```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Login:**

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Protected Route:**

```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

✅ **Secure Passwords** - pbkdf2_sha256 hashing  
✅ **Role System** - user, owner, admin  
✅ **Free Trial** - 60-day trial period  
✅ **Booking System** - Reserve gym sessions  
✅ **Attendance** - Auto-tracked timestamps  
✅ **Multi-Gym** - Owners manage multiple gyms

---

## 📈 Current Status

| Feature         | Status         |
| --------------- | -------------- |
| Project Setup   | ✅ Complete    |
| Database Models | ✅ Complete    |
| Relationships   | ✅ Complete    |
| Migrations      | ✅ Complete    |
| API Routes      | 🔜 Coming Soon |
| Authentication  | 🔜 Coming Soon |

---

**Built with ❤️ using Flask, SQLAlchemy & PostgreSQL**
