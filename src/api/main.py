import sqlite3
import passlib.hash
from aiohttp import web
import jwt
import datetime

# Create an SQLite database (you can change the name)
conn = sqlite3.connect("user_db.sqlite")
cursor = conn.cursor()

# Create a table for storing users
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        username TEXT UNIQUE
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS offices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT
    )
"""
)

# Create the 'reviews' table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_id INTEGER,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        text TEXT,
        FOREIGN KEY (office_id) REFERENCES offices(id)
    )
"""
)

conn.commit()

# Secret key for JWT token, change this to a strong secret in production
SECRET_KEY = "your-secret-key"

app = web.Application()


# Registration handler
async def register(request):
    try:
        data = await request.json()
        print(data)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return web.Response(status=400, text="Email and password are required.")

        # Hash the password before storing it
        hashed_password = passlib.hash.pbkdf2_sha256.using(
            rounds=1000, salt_size=16
        ).hash(password)

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password),
        )
        conn.commit()

        # Create and return a JWT token as the API token
        payload = {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
        }
        api_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return web.json_response({"api_token": api_token})
    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


# Login handler
async def login(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        print(data)

        if not email:
            return web.Response(status=400, text="Email is required.")
        query = "SELECT email, password FROM users WHERE email = ?"
        cursor.execute(query, (email))
        user_data = cursor.fetchone()
        if user_data and passlib.hash.pbkdf2_sha256.verify(password, user_data[2]):
            # Password is correct, create and return a JWT token as the API token
            payload = {
                "email": user_data[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            }
            api_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            print(api_token)
            return web.json_response({"api_token": api_token})
        else:
            return web.Response(
                status=401, text="Invalid email or phone number or password."
            )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


async def passwordchange(request):
    data = await request.json()
    print(data)
    api_token = data.get("api_token")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    new_password_repeat = data.get("new_password_repeat")
    if new_password == new_password_repeat:
        decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms="HS256")
        email = decoded_payload["email"]
        if email:
            query = "SELECT password FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            hashed_password_old = cursor.fetchone()
            print(hashed_password_old)
            if passlib.hash.pbkdf2_sha256.verify(old_password, hashed_password_old[0]):
                hashed_password_new = passlib.hash.pbkdf2_sha256.using(
                    rounds=1000, salt_size=16
                ).hash(new_password)
                cursor.execute(
                    "UPDATE users SET password = ? WHERE email = ?",
                    (hashed_password_new, email),
                )
        print("сделано")
        conn.commit()
        return web.Response(status=200, text=f"Пароль сменен")
    else:
        return web.Response(status=406, text=f"Пароли не совпадают")
    
async def sdfds():
    try:
        cursor.execute("SELECT id, office_id, rating,text FROM reviews")
        user_data = cursor.fetchone()
        # if user_data and passlib.hash.pbkdf2_sha256.verify(password, user_data[2]):
        #     # Password is correct, create and return a JWT token as the API token
        #     payload = {
        #         "email": user_data[0],
        #         "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
        #     }
        #     api_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        #     print(api_token)
        #     return web.json_response({"api_token": api_token})
        # else:
        #     return web.Response(
        #         status=401, text="Invalid email or phone number or password."
        #     )


async def ping(request):
    return web.Response(status=200, text="pong")


app.router.add_post("/register", register)
app.router.add_post("/login", login)
app.router.add_get("/ping", ping)
app.router.add_get("/passwordchange", passwordchange)

if __name__ == "__main__":
    web.run_app(app, host="0.        password = data.get("password")
0.0.0", port=8080)
