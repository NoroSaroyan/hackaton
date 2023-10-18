import sqlite3
import traceback

import passlib.hash
from aiohttp import web
import jwt
import datetime
import requests

import random
import math
import string

from send_email import send_email

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
        name TEXT default NULL,
        surname TEXT default NULL
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


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_id INTEGER,
        user_id INTEGER,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        text TEXT,
        FOREIGN KEY (office_id) REFERENCES offices(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""
)

conn.commit()

# Secret key for JWT token, change this to a strong secret in production
SECRET_KEY = "your-secret-key"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def geocode(address):
    request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json"
    response = requests.get(request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"
        ]
        toponym_coodrinates = toponym["Point"]["pos"]
        coord = " ".join(toponym_coodrinates.split()[::-1])
        return coord


app = web.Application()


async def get_user_profile(request):
    try:
        api_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        if not api_token:
            return web.Response(status=401, text="JWT token missing in headers.")

        try:
            decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return web.Response(status=401, text="JWT token has expired.")
        except jwt.InvalidTokenError:
            return web.Response(status=401, text="Invalid JWT token.")

        # You can now access the user's information from the decoded payload
        email = decoded_payload.get("email")
        if email:
            query = "SELECT email, name, surname FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if user_data:
                user_profile = {
                    "email": user_data[0],
                    "name": user_data[1],
                    "surname": user_data[2],
                }
                return web.json_response(user_profile)
            else:
                return web.Response(status=404, text="User not found.")
        else:
            return web.Response(status=401, text="Invalid JWT token.")

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


# Add the new route
app.router.add_get("/user/profile", get_user_profile)


async def forgot_password(request):
    try:
        data = await request.json()
        email = data.get("email")

        if not email:
            return web.Response(status=400, text="Email is required.")

        # Generate a new random password
        new_password = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )

        # Update the user's password in the database
        hashed_password = passlib.hash.pbkdf2_sha256.using(
            rounds=1000, salt_size=16
        ).hash(new_password)
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?", (hashed_password, email)
        )
        conn.commit()

        # Send the new password by email
        send_email(email, new_password)

        return web.Response(status=200, text="New password sent to your email.")

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


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
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return web.Response(status=500, text=f"Данный email уже зарегистрирован")
        else:
            raise
    except Exception as e:
        traceback.print_exc()
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


async def get_offices_list(request):
    try:
        cursor.execute("SELECT id, address FROM offices")
        offices_list = cursor.fetchall()
        print(offices_list)
        if offices_list:
            out = []
            for id, address in offices_list:
                out.append(
                    {
                        "address": f"город Калуга, {address}",
                        "coords": geocode(f"город Калуга, {address}"),
                        "rating": rating(id)[0],
                        "count_reviews": rating(id)[1],
                    }
                )
            return web.json_response(out)
        else:
            return web.Response(status=404, text="Offices not found.")
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Error: {str(e)}")


def rating(id):
    try:
        cursor.execute("SELECT rating FROM reviews WHERE office_id = ?", (id,))
        rating_list = cursor.fetchall()
        print(rating_list)
        if rating_list:
            return math.ceil(
                sum(list(map(lambda x: int(x[0]), rating_list))) / len(rating_list)
            ), len(rating_list)
        else:
            return 0
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Error: {str(e)}")


async def ping(request):
    return web.Response(status=200, text="pong")


app.router.add_post("/register", register)
app.router.add_post("/login", login)
app.router.add_get("/ping", ping)
app.router.add_get("/passwordchange", passwordchange)
app.router.add_post("/getuserprofile", get_user_profile)
app.router.add_get("/getofficeslist", get_offices_list)


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
