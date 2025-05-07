import requests
import sqlite3
import pandas as pd


categories = ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug",
              "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap", "kill",
              "kick", "happy", "wink", "poke", "dance", "cringe"]


conn = sqlite3.connect("waifu_images.db")
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS images")
cursor.execute("DROP TABLE IF EXISTS categories")


cursor.execute('''
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
)
''')


for idx, name in enumerate(categories, start=1):
    cursor.execute("INSERT INTO categories (category_id, category_name) VALUES (?, ?)", (idx, name))


cursor.execute('''
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    image_url TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
''')


for category in categories:
    for _ in range(5):
        url = f"https://api.waifu.pics/sfw/{category}"
        response = requests.get(url)
        if response.status_code == 200:
            img_url = response.json()["url"]
            cursor.execute("SELECT category_id FROM categories WHERE category_name = ?", (category,))
            category_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO images (category_id, image_url) VALUES (?, ?)", (category_id, img_url))

conn.commit()


df = pd.read_sql_query('''
SELECT c.category_id AS ID, c.category_name AS Category, COUNT(*) AS Count
FROM images i
JOIN categories c ON i.category_id = c.category_id
GROUP BY c.category_id
ORDER BY c.category_id
''', conn)


print("\nจำนวนรูปภาพในแต่ละหมวดหมู่:")
print(df.to_string(index=False))

conn.close()