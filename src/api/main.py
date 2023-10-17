import sqlite3
import passlib.hash
from aiohttp import web
import jwt
import datetime

# Create an SQLite database (you can change the name)
conn = sqlite3.connect('user_db.sqlite')
cursor = conn.cursor()

# Create a table for storing users
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT DEFAULT NULL,
        phone_number TEXT DEFAULT NULL,
        password TEXT)''')
conn.commit()

# Secret key for JWT token, change this to a strong secret in production
SECRET_KEY = 'your-secret-key'

app = web.Application()


# Registration handler
async def register(request):
    try:
        data = await request.json()
        print(data)
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not email and not phone_number or not password:
            return web.Response(status=400,
                                text="Email, phone number, and password are required.")

        # Hash the password before storing it
        hashed_password = passlib.hash.pbkdf2_sha256.using(rounds=1000,
                                                           salt_size=16).hash(
            password)

        cursor.execute(
            'INSERT INTO users (email, phone_number, password) VALUES (?, ?, ?)',
            (email, phone_number, hashed_password))
        conn.commit()

        # Create and return a JWT token as the API token
        payload = {
            'email': email,
            'phone_number': phone_number,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        api_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return web.json_response({'api_token': api_token})
    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


# Login handler
async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not email and not phone_number:
            return web.Response(status=400,
                                text="Email or phone number is required.")

        query = 'SELECT email, phone_number, password FROM users WHERE email = ? OR phone_number = ?'
        cursor.execute(query, (email, phone_number))
        user_data = cursor.fetchone()

        if user_data and passlib.hash.pbkdf2_sha256.verify(password,
                                                           user_data[2]):
            # Password is correct, create and return a JWT token as the API token
            payload = {
                'email': user_data[0],
                'phone_number': user_data[1],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            api_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            return web.json_response({'api_token': api_token})
        else:
            return web.Response(status=401,
                                text="Invalid email or phone number or password.")

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")


async def ping(request):
    return web.Response(status=200, text="pong")


app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_get('/ping', ping)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
