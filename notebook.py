async def passwordchange(request):
    try:
        data = await request.json()
        print(data)
        api_token = data.get('api_token')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password_repeat = data.get('new_password_repeat')
        if new_password == new_password_repeat:
            decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms="HS256")
            email = decoded_payload['email']
            if email:
                query = "SELECT password FROM users WHERE email = ?"
                cursor.execute(query, (email,))
                hashed_password_old = cursor.fetchone()
                print(hashed_password_old)
                if passlib.hash.pbkdf2_sha256.verify(old_password, hashed_password_old[0]):
                    hashed_password_new = passlib.hash.pbkdf2_sha256.using(rounds=1000, salt_size=16).hash(new_password)
                    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password_new, email))
            print('сделано')
            conn.commit()
            return web.Response(status=200, text=f"Пароль сменен")
        else:
            return web.Response(status=406, text=f"Пароли не совпадают")
    except Exception as e:
        return web.Response(status=450, text=f"Error: {str(e)}")


async def review(request):
    try:
        data = await request.json()
        api_token = data.get('api_token')
        office_id = data['office_id']
        rating = data['rating']
        text = data['text']
        decoded_payload = jwt.decode(api_token, SECRET_KEY, algorithms="HS256")
        email = decoded_payload['email']
        query = 'SELECT id FROM users WHERE email = ?'
        cursor.execute(query, (email,))
        user_id = cursor.fetchone()
        query = 'INSERT INTO reviews (office_id, user_id, rating, text) VALUES (?, ?, ?, ?)'
        cursor.execute(query, (office_id, user_id[0], rating, text))
        conn.commit()
        return web.Response(status=200, text=f"Отзыв оставлен")
    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")

async def ping(request):
    return web.Response(status=200, text="pong")


app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_get('/ping', ping)
app.router.add_get('/passwordchange', passwordchange)
app.router.add_get('/review', review)