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


conn = sqlite3.connect("user_db.sqlite")
cursor = conn.cursor()

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
    else:
        return web.Response(status=404, text="Неправильный адресс.")


app = web.Application()


async def get_user_profile(request):
    api_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
    if not api_token:
        return web.Response(status=401, text="JWT отсутсвует в хедерах.")

    try:
        decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return web.Response(status=401, text="JWT токен просрочен.")
    except jwt.InvalidTokenError:
        return web.Response(status=401, text="Неправильный JWT токен.")

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
            return web.Response(status=404, text="Пользователь не найден")
    else:
        return web.Response(status=401, text="Неправильный JWT токен.")



app.router.add_get("/user/profile", get_user_profile)


async def forgot_password(request):
    try:
        data = await request.json()
        email = data.get("email")

        if not email:
            return web.Response(status=400, text="Email обязателен.")

        new_password = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )

        hashed_password = passlib.hash.pbkdf2_sha256.using(
            rounds=1000, salt_size=16
        ).hash(new_password)
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?", (hashed_password, email)
        )
        conn.commit()

        send_email(email, new_password)

        return web.Response(status=200, text="Новый временный пароль отправлен на вашу почту.")

    except Exception as e:
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def register(request):
    try:
        data = await request.json()
        print(data)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return web.Response(status=400, text="Email и пароль обязательны.")

        hashed_password = passlib.hash.pbkdf2_sha256.using(
            rounds=1000, salt_size=16
        ).hash(password)

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password),
        )
        conn.commit()

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
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def login(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        print(data)

        if not email:
            return web.Response(status=400, text="Email обязателен")
        query = "SELECT email, password FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()
        if user_data and passlib.hash.pbkdf2_sha256.verify(password, user_data[1]):
            payload = {
                "email": user_data[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            }
            api_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            print(api_token)
            return web.json_response({"api_token": api_token})
        else:
            return web.Response(status=401, text="Неправильный email или пароль")

    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def addname_and_surname(request):
    try:
        data = await request.json()
        name = data["name"]
        surname = data["surname"]
        api_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        if not api_token:
            return web.Response(status=401, text="JWT токен отсутсвует в хедерах.")
        try:
            decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms=["HS256"])
            email = decoded_payload.get("email")
        except jwt.ExpiredSignatureError:
            return web.Response(status=401, text="JWT токен просрочен")
        except jwt.InvalidTokenError:
            return web.Response(status=401, text="Неправильный JWT токен")
        query = "UPDATE users SET name = ?, surname = ? WHERE email = ?"
        cursor.execute(query, (name, surname, email))
        conn.commit()
        return web.Response(status=200, text=f"Имя и фамилия обновленна")
    except Exception as e:
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def passwordchange(request):
    try:
        api_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        if not api_token:
            return web.Response(status=401, text="JWT отсутствует в хедерах.")
        try:
            decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms=["HS256"])
            email = decoded_payload.get("email")
        except jwt.ExpiredSignatureError:
            return web.Response(status=401, text="JWT просрочен.")
        except jwt.InvalidTokenError:
            return web.Response(status=401, text="Неправильный JWT токен")

        data = await request.json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not email or not old_password or not new_password:
            return web.Response(
                status=400, text="Email, старый пароль, и новый пароль обязательны."
            )

        query = "SELECT password FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        hashed_password_old = cursor.fetchone()

        if hashed_password_old and passlib.hash.pbkdf2_sha256.verify(
            old_password, hashed_password_old[0]
        ):
            hashed_password_new = passlib.hash.pbkdf2_sha256.using(
                rounds=1000, salt_size=16
            ).hash(new_password)
            cursor.execute(
                "UPDATE users SET password = ? WHERE email = ?",
                (hashed_password_new, email),
            )
            conn.commit()

            payload = {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            }
            new_api_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return web.json_response({"api_token": new_api_token})
        else:
            return web.Response(status=401, text="Неверный старый пароль")

    except Exception as e:
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


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
            return web.Response(status=404, text="Отделения не найдены.")
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


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
            return 0, 0
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def review(request):
    try:
        api_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        if not api_token:
            return web.Response(status=401, text="JWT токен отсутсвует в хедерах")
        try:
            decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms=["HS256"])
            email = decoded_payload.get("email")
        except jwt.ExpiredSignatureError:
            return web.Response(status=401, text="JWT токен просрочен.")
        except jwt.InvalidTokenError:
            return web.Response(status=401, text="Неправильный JWT токен.")
        data = await request.json()
        office_id = data["office_id"]
        rating = data["rating"]
        text = data["text"]
        query = "SELECT id FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        user_id = cursor.fetchone()
        query = (
            "INSERT INTO reviews (office_id, user_id, rating, text) VALUES (?, ?, ?, ?)"
        )
        cursor.execute(query, (office_id, user_id[0], rating, text))
        conn.commit()
        return web.Response(status=200, text=f"Отзыв оставлен")
    except Exception as e:
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def get_reviews(request):
    try:
        data = await request.json()
        address = data['address']
        cursor.execute("""SELECT name, surname, rating, text
                       FROM reviews
                       INNER JOIN offices
                       ON reviews.office_id = offices.id
                       INNER JOIN users
                       ON reviews.user_id = users.id
                       WHERE address = ? """, (address,))
        reviews_list = cursor.fetchall()
        print(reviews_list)
        if reviews_list:
            out = []
            for name, surname, rating, text in reviews_list:
                out.append(
                    {
                        "name": f"{name} {surname}",
                        "rating": rating,
                        "text": text,
                    }
                )
            return web.json_response(out)
        else:
            return web.Response(status=404, text="Оценки не найдены.")
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"Ошибка: {str(e)}")


async def ping(request):
    return web.Response(status=200, text="pong")


app.router.add_post("/register", register)
app.router.add_post("/login", login)
app.router.add_get("/ping", ping)
app.router.add_post("/passwordchange", passwordchange)
app.router.add_get("/get_user_profile", get_user_profile)
app.router.add_post("/review", review)
app.router.add_post("/forgot_password", forgot_password)
app.router.add_post("/addname_and_surname", addname_and_surname)
app.router.add_get("/get_offices_list", get_offices_list)
app.router.add_get("/get_reviews", get_reviews)


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
