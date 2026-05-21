import sqlite3
from pathlib import Path

from seed_data import SEED_CAFES


DATABASE_FILE = Path(__file__).parent / "data" / "coffee_run.db"


def connect():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT,
                avatar_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cafes (
                cafe_id TEXT PRIMARY KEY,
                google_place_id TEXT UNIQUE,
                name TEXT NOT NULL,
                area TEXT NOT NULL,
                address TEXT NOT NULL,
                distance_meters INTEGER NOT NULL DEFAULT 0,
                lat REAL,
                lng REAL,
                rating REAL NOT NULL DEFAULT 0,
                user_rating REAL NOT NULL DEFAULT 0,
                tags TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                opening_hours TEXT NOT NULL DEFAULT '',
                website TEXT NOT NULL DEFAULT '',
                maps_url TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT 'seed',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                cafe_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, cafe_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                cafe_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
            );

            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                cafe_id TEXT NOT NULL,
                content TEXT NOT NULL,
                rating INTEGER NOT NULL,
                image_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
            );

            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (post_id, tag),
                FOREIGN KEY (post_id) REFERENCES posts (post_id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (post_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS likes (
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (post_id, user_id),
                FOREIGN KEY (post_id) REFERENCES posts (post_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            """
        )
        migrate_existing_tables(connection)
        seed_cafes(connection)


def migrate_existing_tables(connection):
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(cafes)").fetchall()
    }
    migrations = {
        "google_place_id": "ALTER TABLE cafes ADD COLUMN google_place_id TEXT",
        "lat": "ALTER TABLE cafes ADD COLUMN lat REAL",
        "lng": "ALTER TABLE cafes ADD COLUMN lng REAL",
        "user_rating": "ALTER TABLE cafes ADD COLUMN user_rating REAL NOT NULL DEFAULT 0",
        "opening_hours": "ALTER TABLE cafes ADD COLUMN opening_hours TEXT NOT NULL DEFAULT ''",
        "website": "ALTER TABLE cafes ADD COLUMN website TEXT NOT NULL DEFAULT ''",
        "maps_url": "ALTER TABLE cafes ADD COLUMN maps_url TEXT NOT NULL DEFAULT ''",
        "source": "ALTER TABLE cafes ADD COLUMN source TEXT NOT NULL DEFAULT 'seed'",
        "created_at": "ALTER TABLE cafes ADD COLUMN created_at TEXT",
    }
    for column, statement in migrations.items():
        if column not in columns:
            connection.execute(statement)

    user_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(users)").fetchall()
    }
    if "display_name" not in user_columns:
        connection.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
    if "avatar_path" not in user_columns:
        connection.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT")


def seed_cafes(connection):
    for cafe in SEED_CAFES:
        connection.execute(
            """
            INSERT INTO cafes (
                cafe_id, google_place_id, name, area, address, distance_meters,
                lat, lng, rating, user_rating, tags, description, opening_hours,
                website, maps_url, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cafe_id) DO NOTHING
            """,
            (
                cafe["cafe_id"],
                cafe.get("google_place_id"),
                cafe["name"],
                cafe["area"],
                cafe["address"],
                cafe["distance_meters"],
                cafe["lat"],
                cafe["lng"],
                cafe["rating"],
                0,
                ",".join(cafe["tags"]),
                cafe["description"],
                cafe["opening_hours"],
                cafe["website"],
                cafe["maps_url"],
                "seed",
            ),
        )
        connection.execute(
            """
            UPDATE cafes
            SET
                lat = COALESCE(lat, ?),
                lng = COALESCE(lng, ?),
                opening_hours = CASE WHEN opening_hours = '' THEN ? ELSE opening_hours END,
                website = CASE WHEN website = '' THEN ? ELSE website END,
                maps_url = CASE WHEN maps_url = '' THEN ? ELSE maps_url END
            WHERE cafe_id = ?
            """,
            (
                cafe["lat"],
                cafe["lng"],
                cafe["opening_hours"],
                cafe["website"],
                cafe["maps_url"],
                cafe["cafe_id"],
            ),
        )


def split_tags(tags):
    if isinstance(tags, list):
        return tags
    return [tag for tag in (tags or "").split(",") if tag]


def row_to_cafe(row):
    cafe = dict(row)
    cafe["tags"] = split_tags(cafe.get("tags"))
    return cafe


def get_or_create_user(username):
    cleaned_username = username.strip()
    if not cleaned_username:
        return None

    with connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO users (username, display_name)
            VALUES (?, ?)
            """,
            (cleaned_username, cleaned_username),
        )
        row = connection.execute(
            """
            SELECT user_id, username, display_name, avatar_path
            FROM users
            WHERE username = ?
            """,
            (cleaned_username,),
        ).fetchone()
        return dict(row)


def update_user_profile(user_id, display_name, avatar_path=None):
    with connect() as connection:
        if avatar_path:
            connection.execute(
                "UPDATE users SET display_name = ?, avatar_path = ? WHERE user_id = ?",
                (display_name.strip(), avatar_path, user_id),
            )
        else:
            connection.execute(
                "UPDATE users SET display_name = ? WHERE user_id = ?",
                (display_name.strip(), user_id),
            )


def get_user(user_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT user_id, username, display_name, avatar_path FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def upsert_cafe(cafe):
    cafe_id = cafe.get("cafe_id") or cafe.get("google_place_id")
    if not cafe_id:
        raise ValueError("Cafe must have cafe_id or google_place_id")

    tags = cafe.get("tags", [])
    if isinstance(tags, list):
        tags = ",".join(tags)

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO cafes (
                cafe_id, google_place_id, name, area, address, distance_meters,
                lat, lng, rating, user_rating, tags, description, opening_hours,
                website, maps_url, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cafe_id) DO UPDATE SET
                google_place_id = excluded.google_place_id,
                name = excluded.name,
                area = excluded.area,
                address = excluded.address,
                distance_meters = excluded.distance_meters,
                lat = excluded.lat,
                lng = excluded.lng,
                rating = excluded.rating,
                tags = CASE
                    WHEN cafes.tags = '' THEN excluded.tags
                    ELSE cafes.tags
                END,
                description = excluded.description,
                opening_hours = excluded.opening_hours,
                website = excluded.website,
                maps_url = excluded.maps_url,
                source = excluded.source
            """,
            (
                cafe_id,
                cafe.get("google_place_id"),
                cafe.get("name", "未命名咖啡廳"),
                cafe.get("area", "未知"),
                cafe.get("address", ""),
                cafe.get("distance_meters", 0),
                cafe.get("lat"),
                cafe.get("lng"),
                cafe.get("rating", 0),
                cafe.get("user_rating", 0),
                tags,
                cafe.get("description", ""),
                cafe.get("opening_hours", ""),
                cafe.get("website", ""),
                cafe.get("maps_url", ""),
                cafe.get("source", "manual"),
            ),
        )
    return cafe_id


def list_cafes():
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM cafes
            ORDER BY
                CASE WHEN user_rating > 0 THEN user_rating ELSE rating END DESC,
                distance_meters ASC
            """
        ).fetchall()
    return [row_to_cafe(row) for row in rows]


def get_cafe(cafe_id):
    with connect() as connection:
        row = connection.execute("SELECT * FROM cafes WHERE cafe_id = ?", (cafe_id,)).fetchone()
    return row_to_cafe(row) if row else None


def list_areas():
    with connect() as connection:
        rows = connection.execute("SELECT DISTINCT area FROM cafes ORDER BY area").fetchall()
    return [row["area"] for row in rows]


def list_all_tags():
    tags = set()
    for cafe in list_cafes():
        tags.update(cafe["tags"])
    with connect() as connection:
        rows = connection.execute("SELECT DISTINCT tag FROM post_tags ORDER BY tag").fetchall()
    tags.update(row["tag"] for row in rows)
    return sorted(tags)


def get_favorite_ids(user_id):
    with connect() as connection:
        rows = connection.execute(
            "SELECT cafe_id FROM favorites WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    return {row["cafe_id"] for row in rows}


def add_favorite(user_id, cafe_id):
    with connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO favorites (user_id, cafe_id) VALUES (?, ?)",
            (user_id, cafe_id),
        )


def remove_favorite(user_id, cafe_id):
    with connect() as connection:
        connection.execute(
            "DELETE FROM favorites WHERE user_id = ? AND cafe_id = ?",
            (user_id, cafe_id),
        )


def list_favorite_cafes(user_id):
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT cafes.*
            FROM favorites
            JOIN cafes ON cafes.cafe_id = favorites.cafe_id
            WHERE favorites.user_id = ?
            ORDER BY favorites.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [row_to_cafe(row) for row in rows]


def add_review(user_id, cafe_id, rating, note):
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO reviews (user_id, cafe_id, rating, note)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, cafe_id, rating, note.strip()),
        )
    refresh_cafe_user_rating(cafe_id)


def list_reviews(user_id):
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT reviews.*, cafes.name AS cafe_name
            FROM reviews
            JOIN cafes ON cafes.cafe_id = reviews.cafe_id
            WHERE reviews.user_id = ?
            ORDER BY reviews.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_post(user_id, cafe_id, content, rating, image_path, tags):
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO posts (user_id, cafe_id, content, rating, image_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, cafe_id, content.strip(), rating, image_path),
        )
        post_id = cursor.lastrowid
        for tag in tags:
            cleaned_tag = tag.strip()
            if cleaned_tag:
                connection.execute(
                    "INSERT OR IGNORE INTO post_tags (post_id, tag) VALUES (?, ?)",
                    (post_id, cleaned_tag),
                )
    refresh_cafe_user_rating(cafe_id)
    refresh_cafe_tags(cafe_id)
    return post_id


def list_posts(cafe_id=None):
    params = []
    cafe_filter = ""
    if cafe_id:
        cafe_filter = "WHERE posts.cafe_id = ?"
        params.append(cafe_id)

    with connect() as connection:
        rows = connection.execute(
            f"""
            SELECT
                posts.*,
                users.username,
                users.display_name,
                users.avatar_path,
                cafes.name AS cafe_name,
                cafes.area AS cafe_area,
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count,
                (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) AS comment_count
            FROM posts
            JOIN users ON users.user_id = posts.user_id
            JOIN cafes ON cafes.cafe_id = posts.cafe_id
            {cafe_filter}
            ORDER BY posts.created_at DESC
            """,
            params,
        ).fetchall()
        posts = [dict(row) for row in rows]
        for post in posts:
            tag_rows = connection.execute(
                "SELECT tag FROM post_tags WHERE post_id = ? ORDER BY tag",
                (post["post_id"],),
            ).fetchall()
            post["tags"] = [row["tag"] for row in tag_rows]
    return posts


def user_liked_post(user_id, post_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?",
            (user_id, post_id),
        ).fetchone()
    return row is not None


def toggle_like(user_id, post_id):
    with connect() as connection:
        existing = connection.execute(
            "SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?",
            (user_id, post_id),
        ).fetchone()
        if existing:
            connection.execute(
                "DELETE FROM likes WHERE user_id = ? AND post_id = ?",
                (user_id, post_id),
            )
        else:
            connection.execute(
                "INSERT INTO likes (user_id, post_id) VALUES (?, ?)",
                (user_id, post_id),
            )


def add_comment(user_id, post_id, content):
    with connect() as connection:
        connection.execute(
            "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
            (post_id, user_id, content.strip()),
        )


def list_comments(post_id):
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT comments.*, users.username, users.display_name
            FROM comments
            JOIN users ON users.user_id = comments.user_id
            WHERE comments.post_id = ?
            ORDER BY comments.created_at ASC
            """,
            (post_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def refresh_cafe_user_rating(cafe_id):
    with connect() as connection:
        review_avg = connection.execute(
            """
            SELECT AVG(rating)
            FROM (
                SELECT rating FROM reviews WHERE cafe_id = ?
                UNION ALL
                SELECT rating FROM posts WHERE cafe_id = ?
            )
            """,
            (cafe_id, cafe_id),
        ).fetchone()[0]
        connection.execute(
            "UPDATE cafes SET user_rating = ? WHERE cafe_id = ?",
            (review_avg or 0, cafe_id),
        )


def refresh_cafe_tags(cafe_id):
    with connect() as connection:
        current = connection.execute(
            "SELECT tags FROM cafes WHERE cafe_id = ?",
            (cafe_id,),
        ).fetchone()
        if not current:
            return
        tags = set(split_tags(current["tags"]))
        rows = connection.execute(
            """
            SELECT DISTINCT post_tags.tag
            FROM post_tags
            JOIN posts ON posts.post_id = post_tags.post_id
            WHERE posts.cafe_id = ?
            """,
            (cafe_id,),
        ).fetchall()
        tags.update(row["tag"] for row in rows)
        connection.execute(
            "UPDATE cafes SET tags = ? WHERE cafe_id = ?",
            (",".join(sorted(tags)), cafe_id),
        )


def get_user_stats(user_id):
    with connect() as connection:
        favorite_count = connection.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
        post_count = connection.execute(
            "SELECT COUNT(*) FROM posts WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
        footprint_count = connection.execute(
            "SELECT COUNT(DISTINCT cafe_id) FROM posts WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
        review_count = connection.execute(
            "SELECT COUNT(*) FROM reviews WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
    return {
        "favorite_count": favorite_count,
        "post_count": post_count,
        "footprint_count": footprint_count,
        "review_count": review_count,
    }


def list_footprint_cafes(user_id):
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT cafes.*
            FROM posts
            JOIN cafes ON cafes.cafe_id = posts.cafe_id
            WHERE posts.user_id = ?
            ORDER BY cafes.name
            """,
            (user_id,),
        ).fetchall()
    return [row_to_cafe(row) for row in rows]
