"""Persistence layer for Coffee Run.

Set ``SUPABASE_DB_URL`` to use shared Supabase PostgreSQL storage. Without it,
the app keeps using its local SQLite database so UI development remains usable.
All page modules call this repository layer instead of executing SQL directly.
"""

import os
import sqlite3
from pathlib import Path

import streamlit as st

from seed_data import SEED_CAFES


DATABASE_FILE = Path(__file__).parent / "data" / "coffee_run.db"
TRAIT_FIELDS = (
    "has_outlets_score",
    "no_time_limit_score",
    "quiet_score",
    "study_score",
    "chat_score",
    "dessert_score",
    "price_score",
    "open_late_score",
)


def configured_postgres_url():
    """Read the Supabase Postgres connection string from private settings."""
    value = os.environ.get("SUPABASE_DB_URL", "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get("SUPABASE_DB_URL", "")).strip()
    except Exception:
        return ""


def using_supabase():
    """Return whether this run stores records in Supabase PostgreSQL."""
    return bool(configured_postgres_url())


def database_label():
    """Return a user-facing storage description for the settings screen."""
    return "Supabase PostgreSQL（多人共用）" if using_supabase() else "本機 SQLite（尚未連接 Supabase）"


class DatabaseConnection:
    """Small compatibility wrapper for SQLite and PostgreSQL connections."""

    def __init__(self, raw_connection, is_postgres=False):
        self.raw_connection = raw_connection
        self.is_postgres = is_postgres

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        if exception_type:
            self.raw_connection.rollback()
        else:
            self.raw_connection.commit()
        self.raw_connection.close()

    def _sql(self, statement):
        if self.is_postgres:
            return statement.replace("?", "%s")
        return statement

    def execute(self, statement, params=()):
        return self.raw_connection.execute(self._sql(statement), params)

    def executescript(self, script):
        if self.is_postgres:
            return self.raw_connection.execute(script)
        return self.raw_connection.executescript(script)


def connect():
    """Open the configured database and return dictionary-compatible rows."""
    postgres_url = configured_postgres_url()
    if postgres_url:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as error:
            raise RuntimeError("Supabase 模式需要安裝 psycopg：python3 -m pip install -r requirements.txt") from error
        raw_connection = psycopg.connect(postgres_url, row_factory=dict_row, prepare_threshold=None)
        return DatabaseConnection(raw_connection, is_postgres=True)

    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    raw_connection = sqlite3.connect(DATABASE_FILE)
    raw_connection.row_factory = sqlite3.Row
    raw_connection.execute("PRAGMA foreign_keys = ON")
    return DatabaseConnection(raw_connection)


def initialize_database():
    """Create current tables, migrate old demo databases, and seed cafes."""
    with connect() as connection:
        schema = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT,
                avatar_path TEXT,
                bio TEXT NOT NULL DEFAULT '',
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
                open_now INTEGER,
                website TEXT NOT NULL DEFAULT '',
                maps_url TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT 'seed',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                image_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
            );

            CREATE TABLE IF NOT EXISTS post_photos (
                photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (post_id)
            );

            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (post_id, tag),
                FOREIGN KEY (post_id) REFERENCES posts (post_id)
            );

            CREATE TABLE IF NOT EXISTS post_trait_feedback (
                post_id INTEGER PRIMARY KEY,
                cafe_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                has_outlets INTEGER,
                no_time_limit INTEGER,
                quiet_score INTEGER,
                study_score INTEGER,
                chat_score INTEGER,
                dessert_score INTEGER,
                price_score INTEGER,
                open_late INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (post_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS cafe_traits (
                cafe_id TEXT PRIMARY KEY,
                has_outlets_score REAL NOT NULL DEFAULT 0,
                no_time_limit_score REAL NOT NULL DEFAULT 0,
                quiet_score REAL NOT NULL DEFAULT 0,
                study_score REAL NOT NULL DEFAULT 0,
                chat_score REAL NOT NULL DEFAULT 0,
                dessert_score REAL NOT NULL DEFAULT 0,
                price_score REAL NOT NULL DEFAULT 0,
                open_late_score REAL NOT NULL DEFAULT 0,
                feedback_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
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
        if connection.is_postgres:
            schema = schema.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
            schema = schema.replace("TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP", "TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP")
        connection.executescript(schema)
        migrate_existing_tables(connection)
        seed_cafes(connection)
        seed_cafe_traits(connection)
        seed_demo_social_data(connection)


def migrate_existing_tables(connection):
    """Add columns needed by new screens when an older database exists."""
    if connection.is_postgres:
        for statement in (
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS google_place_id TEXT",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS lat REAL",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS lng REAL",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS user_rating REAL NOT NULL DEFAULT 0",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS opening_hours TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS open_now INTEGER",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS website TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS maps_url TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'seed'",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS created_at TEXT",
            "ALTER TABLE cafes ADD COLUMN IF NOT EXISTS updated_at TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_path TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT NOT NULL DEFAULT ''",
        ):
            connection.execute(statement)
        return

    cafe_columns = {row["name"] for row in connection.execute("PRAGMA table_info(cafes)").fetchall()}
    cafe_migrations = {
        "google_place_id": "ALTER TABLE cafes ADD COLUMN google_place_id TEXT",
        "lat": "ALTER TABLE cafes ADD COLUMN lat REAL",
        "lng": "ALTER TABLE cafes ADD COLUMN lng REAL",
        "user_rating": "ALTER TABLE cafes ADD COLUMN user_rating REAL NOT NULL DEFAULT 0",
        "opening_hours": "ALTER TABLE cafes ADD COLUMN opening_hours TEXT NOT NULL DEFAULT ''",
        "open_now": "ALTER TABLE cafes ADD COLUMN open_now INTEGER",
        "website": "ALTER TABLE cafes ADD COLUMN website TEXT NOT NULL DEFAULT ''",
        "maps_url": "ALTER TABLE cafes ADD COLUMN maps_url TEXT NOT NULL DEFAULT ''",
        "source": "ALTER TABLE cafes ADD COLUMN source TEXT NOT NULL DEFAULT 'seed'",
        "created_at": "ALTER TABLE cafes ADD COLUMN created_at TEXT",
        "updated_at": "ALTER TABLE cafes ADD COLUMN updated_at TEXT",
    }
    for column, statement in cafe_migrations.items():
        if column not in cafe_columns:
            connection.execute(statement)

    user_columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()}
    user_migrations = {
        "display_name": "ALTER TABLE users ADD COLUMN display_name TEXT",
        "avatar_path": "ALTER TABLE users ADD COLUMN avatar_path TEXT",
        "bio": "ALTER TABLE users ADD COLUMN bio TEXT NOT NULL DEFAULT ''",
    }
    for column, statement in user_migrations.items():
        if column not in user_columns:
            connection.execute(statement)


def seed_cafes(connection):
    """Insert initial cafes without overwriting user-generated data."""
    for cafe in SEED_CAFES:
        connection.execute(
            """
            INSERT INTO cafes (
                cafe_id, google_place_id, name, area, address, distance_meters,
                lat, lng, rating, user_rating, tags, description, opening_hours,
                open_now, website, maps_url, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                cafe.get("open_now"),
                cafe["website"],
                cafe["maps_url"],
                "seed",
            ),
        )
        connection.execute(
            """
            UPDATE cafes
            SET lat = COALESCE(lat, ?),
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


def seed_cafe_traits(connection):
    """Create useful filter traits for seed cafes based on their labels."""
    for cafe in SEED_CAFES:
        tags = set(cafe["tags"])
        connection.execute(
            """
            INSERT INTO cafe_traits (
                cafe_id, has_outlets_score, no_time_limit_score, quiet_score,
                study_score, chat_score, dessert_score, price_score,
                open_late_score, feedback_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(cafe_id) DO NOTHING
            """,
            (
                cafe["cafe_id"],
                1 if "插座" in tags else 0,
                1 if "不限時" in tags else 0,
                5 if "安靜" in tags else 2,
                5 if "適合讀書" in tags or "讀書" in tags else 2,
                5 if "適合聊天" in tags or "聚會" in tags else 2,
                5 if "甜點" in tags else 2,
                5 if "平價" in tags else 2,
                1 if "晚上營業" in tags else 0,
            ),
        )


def seed_demo_social_data(connection):
    """Seed lightweight community activity so a fresh demo is not empty."""
    demo_posts = [
        ("coffee_daily", "cafe-001", "窗邊很安靜，插座位置也夠，適合帶電腦來讀書。", 5, ["安靜", "插座多", "適合讀書"]),
        ("late_latte", "cafe-005", "晚上想聊天或吃甜點時很方便，氣氛舒服。", 4, ["深夜咖啡廳", "甜點", "適合聊天"]),
        ("campus_cup", "cafe-006", "不限時又適合學生，小組討論不會有壓力。", 5, ["不限時", "學生友善", "插座多"]),
    ]
    for username, cafe_id, content, rating, tags in demo_posts:
        connection.execute(
            "INSERT INTO users (username, display_name, bio) VALUES (?, ?, ?) ON CONFLICT(username) DO NOTHING",
            (username, username, "分享日常咖啡探店紀錄"),
        )
        user_id = connection.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()["user_id"]
        existing = connection.execute(
            "SELECT post_id FROM posts WHERE user_id = ? AND cafe_id = ? AND content = ?",
            (user_id, cafe_id, content),
        ).fetchone()
        if existing:
            continue
        post_id = insert_and_get_id(
            connection,
            "INSERT INTO posts (user_id, cafe_id, content, rating) VALUES (?, ?, ?, ?)",
            (user_id, cafe_id, content, rating),
            "post_id",
        )
        for tag in tags:
            connection.execute(
                "INSERT INTO post_tags (post_id, tag) VALUES (?, ?) ON CONFLICT(post_id, tag) DO NOTHING",
                (post_id, tag),
            )
        connection.execute(
            "INSERT INTO likes (post_id, user_id) VALUES (?, ?) ON CONFLICT(post_id, user_id) DO NOTHING",
            (post_id, user_id),
        )
        connection.execute(
            "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
            (post_id, user_id, "推薦收藏這間店！"),
        )


def split_tags(tags):
    """Normalize comma-separated tag strings into a list."""
    if isinstance(tags, list):
        return tags
    return [tag for tag in (tags or "").split(",") if tag]


def insert_and_get_id(connection, statement, params, primary_key):
    """Insert a row and return its generated primary key on either backend."""
    if connection.is_postgres:
        row = connection.execute(f"{statement} RETURNING {primary_key}", params).fetchone()
        return row[primary_key]
    cursor = connection.execute(statement, params)
    return cursor.lastrowid


def row_to_cafe(row):
    """Convert a database cafe row into the dictionary consumed by pages."""
    cafe = dict(row)
    cafe["tags"] = split_tags(cafe.get("tags"))
    return cafe


def get_or_create_user(username):
    """Return an existing user or create one for demo sign in."""
    cleaned_username = username.strip()
    if not cleaned_username:
        return None
    with connect() as connection:
        connection.execute(
            "INSERT INTO users (username, display_name) VALUES (?, ?) ON CONFLICT(username) DO NOTHING",
            (cleaned_username, cleaned_username),
        )
        row = connection.execute(
            "SELECT user_id, username, display_name, avatar_path, bio FROM users WHERE username = ?",
            (cleaned_username,),
        ).fetchone()
    return dict(row)


def update_user_profile(user_id, display_name, bio="", avatar_path=None):
    """Update editable personal profile fields."""
    display_name = display_name.strip() or "Coffee Runner"
    with connect() as connection:
        if avatar_path:
            connection.execute(
                "UPDATE users SET display_name = ?, bio = ?, avatar_path = ? WHERE user_id = ?",
                (display_name, bio.strip(), avatar_path, user_id),
            )
        else:
            connection.execute(
                "UPDATE users SET display_name = ?, bio = ? WHERE user_id = ?",
                (display_name, bio.strip(), user_id),
            )


def get_user(user_id):
    """Fetch one user by primary key."""
    with connect() as connection:
        row = connection.execute(
            "SELECT user_id, username, display_name, avatar_path, bio FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def upsert_cafe(cafe):
    """Insert or update a cafe imported from Google or local seed data."""
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
                open_now, website, maps_url, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cafe_id) DO UPDATE SET
                google_place_id = COALESCE(excluded.google_place_id, cafes.google_place_id),
                name = excluded.name,
                area = excluded.area,
                address = excluded.address,
                distance_meters = excluded.distance_meters,
                lat = excluded.lat,
                lng = excluded.lng,
                rating = excluded.rating,
                tags = CASE WHEN cafes.tags = '' THEN excluded.tags ELSE cafes.tags END,
                description = excluded.description,
                opening_hours = excluded.opening_hours,
                open_now = excluded.open_now,
                website = excluded.website,
                maps_url = excluded.maps_url,
                source = excluded.source,
                updated_at = CURRENT_TIMESTAMP
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
                cafe.get("open_now"),
                cafe.get("website", ""),
                cafe.get("maps_url", ""),
                cafe.get("source", "manual"),
            ),
        )
        connection.execute(
            "INSERT INTO cafe_traits (cafe_id) VALUES (?) ON CONFLICT(cafe_id) DO NOTHING",
            (cafe_id,),
        )
    return cafe_id


def _cafe_query(where_clause="", params=(), order_clause=""):
    """Return cafe rows joined with aggregate traits."""
    with connect() as connection:
        rows = connection.execute(
            f"""
            SELECT cafes.*, cafe_traits.has_outlets_score, cafe_traits.no_time_limit_score,
                   cafe_traits.quiet_score, cafe_traits.study_score, cafe_traits.chat_score,
                   cafe_traits.dessert_score, cafe_traits.price_score,
                   cafe_traits.open_late_score, cafe_traits.feedback_count
            FROM cafes
            LEFT JOIN cafe_traits ON cafe_traits.cafe_id = cafes.cafe_id
            {where_clause}
            {order_clause}
            """,
            params,
        ).fetchall()
    return [row_to_cafe(row) for row in rows]


def list_cafes():
    """List cafes ordered by the best visible rating and distance."""
    return _cafe_query(
        order_clause="""
        ORDER BY CASE WHEN user_rating > 0 THEN user_rating ELSE rating END DESC,
                 distance_meters ASC
        """
    )


def get_cafe(cafe_id):
    """Fetch one cafe with its current trait aggregate."""
    cafes = _cafe_query("WHERE cafes.cafe_id = ?", (cafe_id,))
    return cafes[0] if cafes else None


def list_areas():
    """Return distinct areas used in explore filters."""
    with connect() as connection:
        rows = connection.execute("SELECT DISTINCT area FROM cafes ORDER BY area").fetchall()
    return [row["area"] for row in rows]


def list_all_tags():
    """Return all cafe and post tags available for filters."""
    tags = set()
    for cafe in list_cafes():
        tags.update(cafe["tags"])
    with connect() as connection:
        rows = connection.execute("SELECT DISTINCT tag FROM post_tags ORDER BY tag").fetchall()
    tags.update(row["tag"] for row in rows)
    return sorted(tags)


def get_favorite_ids(user_id):
    """Return current user's favorite cafe IDs."""
    with connect() as connection:
        rows = connection.execute("SELECT cafe_id FROM favorites WHERE user_id = ?", (user_id,)).fetchall()
    return {row["cafe_id"] for row in rows}


def add_favorite(user_id, cafe_id):
    """Save a cafe to the user's collection."""
    with connect() as connection:
        connection.execute(
            "INSERT INTO favorites (user_id, cafe_id) VALUES (?, ?) ON CONFLICT(user_id, cafe_id) DO NOTHING",
            (user_id, cafe_id),
        )


def remove_favorite(user_id, cafe_id):
    """Remove a cafe from the user's collection."""
    with connect() as connection:
        connection.execute("DELETE FROM favorites WHERE user_id = ? AND cafe_id = ?", (user_id, cafe_id))


def list_favorite_cafes(user_id):
    """List cafes favorited by one user."""
    return _cafe_query(
        "JOIN favorites ON favorites.cafe_id = cafes.cafe_id WHERE favorites.user_id = ?",
        (user_id,),
        "ORDER BY favorites.created_at DESC",
    )


def add_review(user_id, cafe_id, rating, note):
    """Preserve legacy review support and refresh cafe average."""
    with connect() as connection:
        connection.execute(
            "INSERT INTO reviews (user_id, cafe_id, rating, note) VALUES (?, ?, ?, ?)",
            (user_id, cafe_id, rating, note.strip()),
        )
    refresh_cafe_user_rating(cafe_id)


def list_reviews(user_id):
    """List legacy reviews written by one user."""
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT reviews.*, cafes.name AS cafe_name
            FROM reviews JOIN cafes ON cafes.cafe_id = reviews.cafe_id
            WHERE reviews.user_id = ? ORDER BY reviews.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_post(user_id, cafe_id, content, rating, image_paths=None, tags=None, feedback=None):
    """Create a cafe-linked post with photos, tags, and filter feedback."""
    content = content.strip()
    if not content:
        raise ValueError("貼文內容不可空白")
    if rating not in range(1, 6):
        raise ValueError("評分必須在 1 至 5 之間")
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    image_paths = [path for path in (image_paths or []) if path]
    tags = tags or []
    feedback = feedback or {}

    with connect() as connection:
        post_id = insert_and_get_id(
            connection,
            "INSERT INTO posts (user_id, cafe_id, content, rating, image_path) VALUES (?, ?, ?, ?, ?)",
            (user_id, cafe_id, content, rating, image_paths[0] if image_paths else None),
            "post_id",
        )
        for order, image_path in enumerate(image_paths):
            connection.execute(
                "INSERT INTO post_photos (post_id, image_path, sort_order) VALUES (?, ?, ?)",
                (post_id, image_path, order),
            )
        for tag in tags:
            cleaned_tag = tag.strip()
            if cleaned_tag:
                connection.execute(
                    "INSERT INTO post_tags (post_id, tag) VALUES (?, ?) ON CONFLICT(post_id, tag) DO NOTHING",
                    (post_id, cleaned_tag),
                )
        if feedback:
            connection.execute(
                """
                INSERT INTO post_trait_feedback (
                    post_id, cafe_id, user_id, has_outlets, no_time_limit,
                    quiet_score, study_score, chat_score, dessert_score,
                    price_score, open_late
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    post_id,
                    cafe_id,
                    user_id,
                    feedback.get("has_outlets"),
                    feedback.get("no_time_limit"),
                    feedback.get("quiet_score"),
                    feedback.get("study_score"),
                    feedback.get("chat_score"),
                    feedback.get("dessert_score"),
                    feedback.get("price_score"),
                    feedback.get("open_late"),
                ),
            )
    refresh_cafe_user_rating(cafe_id)
    refresh_cafe_tags(cafe_id)
    refresh_cafe_traits(cafe_id)
    return post_id


def _post_query(where_clause="", params=(), order_clause="ORDER BY posts.created_at DESC"):
    """Return social post view models with interaction counts and tags."""
    with connect() as connection:
        rows = connection.execute(
            f"""
            SELECT posts.*, users.username, users.display_name, users.avatar_path,
                   cafes.name AS cafe_name, cafes.area AS cafe_area,
                   (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count,
                   (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) AS comment_count
            FROM posts
            JOIN users ON users.user_id = posts.user_id
            JOIN cafes ON cafes.cafe_id = posts.cafe_id
            {where_clause}
            {order_clause}
            """,
            params,
        ).fetchall()
        posts = [dict(row) for row in rows]
        for post in posts:
            tag_rows = connection.execute("SELECT tag FROM post_tags WHERE post_id = ? ORDER BY tag", (post["post_id"],)).fetchall()
            photo_rows = connection.execute(
                "SELECT image_path FROM post_photos WHERE post_id = ? ORDER BY sort_order",
                (post["post_id"],),
            ).fetchall()
            post["tags"] = [row["tag"] for row in tag_rows]
            post["photos"] = [row["image_path"] for row in photo_rows]
            if not post["photos"] and post.get("image_path"):
                post["photos"] = [post["image_path"]]
    return posts


def list_posts(cafe_id=None, user_id=None, search="", sort_by="latest"):
    """List feed posts with optional cafe, user, and text filtering."""
    conditions = []
    params = []
    if cafe_id:
        conditions.append("posts.cafe_id = ?")
        params.append(cafe_id)
    if user_id:
        conditions.append("posts.user_id = ?")
        params.append(user_id)
    if search.strip():
        conditions.append("(cafes.name LIKE ? OR posts.content LIKE ? OR users.username LIKE ?)")
        value = f"%{search.strip()}%"
        params.extend([value, value, value])
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    if sort_by == "熱門":
        order_clause = "ORDER BY like_count DESC, posts.created_at DESC"
    else:
        order_clause = "ORDER BY posts.created_at DESC"
    return _post_query(where_clause, tuple(params), order_clause)


def get_post(post_id):
    """Fetch one social post for the detail screen."""
    posts = _post_query("WHERE posts.post_id = ?", (post_id,), "")
    return posts[0] if posts else None


def get_cafe_photos(cafe_id, limit=6):
    """Use community post photos as the cafe's detail gallery."""
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT image_path, MAX(created_at) AS latest_created_at FROM (
                SELECT post_photos.image_path, posts.created_at, post_photos.sort_order
                FROM post_photos JOIN posts ON posts.post_id = post_photos.post_id
                WHERE posts.cafe_id = ?
                UNION ALL
                SELECT posts.image_path, posts.created_at, 0
                FROM posts
                WHERE posts.cafe_id = ? AND posts.image_path IS NOT NULL
            )
            WHERE image_path IS NOT NULL
            GROUP BY image_path
            ORDER BY MAX(created_at) DESC
            LIMIT ?
            """,
            (cafe_id, cafe_id, limit),
        ).fetchall()
    return [row["image_path"] for row in rows]


def user_liked_post(user_id, post_id):
    """Return whether a user has liked a post."""
    with connect() as connection:
        row = connection.execute("SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id)).fetchone()
    return row is not None


def toggle_like(user_id, post_id):
    """Toggle a user's like for a post."""
    with connect() as connection:
        existing = connection.execute("SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id)).fetchone()
        if existing:
            connection.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        else:
            connection.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))


def add_comment(user_id, post_id, content):
    """Attach a non-empty comment to a post."""
    if content.strip():
        with connect() as connection:
            connection.execute(
                "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
                (post_id, user_id, content.strip()),
            )


def list_comments(post_id):
    """List comments for one post in chronological order."""
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT comments.*, users.username, users.display_name
            FROM comments JOIN users ON users.user_id = comments.user_id
            WHERE comments.post_id = ? ORDER BY comments.created_at ASC
            """,
            (post_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def refresh_cafe_user_rating(cafe_id):
    """Recalculate a cafe's average site rating from reviews and posts."""
    with connect() as connection:
        average = connection.execute(
            """
            SELECT AVG(rating) AS average_rating FROM (
                SELECT rating FROM reviews WHERE cafe_id = ?
                UNION ALL SELECT rating FROM posts WHERE cafe_id = ?
            )
            """,
            (cafe_id, cafe_id),
        ).fetchone()["average_rating"]
        connection.execute("UPDATE cafes SET user_rating = ? WHERE cafe_id = ?", (average or 0, cafe_id))


def refresh_cafe_tags(cafe_id):
    """Merge post labels into the cafe's searchable tag cache."""
    with connect() as connection:
        current = connection.execute("SELECT tags FROM cafes WHERE cafe_id = ?", (cafe_id,)).fetchone()
        if not current:
            return
        tags = set(split_tags(current["tags"]))
        rows = connection.execute(
            """
            SELECT DISTINCT post_tags.tag FROM post_tags
            JOIN posts ON posts.post_id = post_tags.post_id
            WHERE posts.cafe_id = ?
            """,
            (cafe_id,),
        ).fetchall()
        tags.update(row["tag"] for row in rows)
        connection.execute("UPDATE cafes SET tags = ? WHERE cafe_id = ?", (",".join(sorted(tags)), cafe_id))


def refresh_cafe_traits(cafe_id):
    """Aggregate structured post feedback for explore-page filters."""
    with connect() as connection:
        row = connection.execute(
            """
            SELECT AVG(has_outlets) AS has_outlets_score,
                   AVG(no_time_limit) AS no_time_limit_score,
                   AVG(quiet_score) AS quiet_score,
                   AVG(study_score) AS study_score,
                   AVG(chat_score) AS chat_score,
                   AVG(dessert_score) AS dessert_score,
                   AVG(price_score) AS price_score,
                   AVG(open_late) AS open_late_score,
                   COUNT(*) AS feedback_count
            FROM post_trait_feedback WHERE cafe_id = ?
            """,
            (cafe_id,),
        ).fetchone()
        if not row or not row["feedback_count"]:
            return
        aggregate_fields = (
            "has_outlets_score",
            "no_time_limit_score",
            "quiet_score",
            "study_score",
            "chat_score",
            "dessert_score",
            "price_score",
            "open_late_score",
        )
        connection.execute(
            """
            INSERT INTO cafe_traits (
                cafe_id, has_outlets_score, no_time_limit_score, quiet_score,
                study_score, chat_score, dessert_score, price_score,
                open_late_score, feedback_count, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(cafe_id) DO UPDATE SET
                has_outlets_score = excluded.has_outlets_score,
                no_time_limit_score = excluded.no_time_limit_score,
                quiet_score = excluded.quiet_score,
                study_score = excluded.study_score,
                chat_score = excluded.chat_score,
                dessert_score = excluded.dessert_score,
                price_score = excluded.price_score,
                open_late_score = excluded.open_late_score,
                feedback_count = excluded.feedback_count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (cafe_id, *(row[field] or 0 for field in aggregate_fields), row["feedback_count"]),
        )


def get_user_stats(user_id):
    """Return profile statistics."""
    with connect() as connection:
        favorite_count = connection.execute(
            "SELECT COUNT(*) AS count FROM favorites WHERE user_id = ?", (user_id,)
        ).fetchone()["count"]
        post_count = connection.execute(
            "SELECT COUNT(*) AS count FROM posts WHERE user_id = ?", (user_id,)
        ).fetchone()["count"]
        footprint_count = connection.execute(
            "SELECT COUNT(DISTINCT cafe_id) AS count FROM posts WHERE user_id = ?", (user_id,)
        ).fetchone()["count"]
    return {"favorite_count": favorite_count, "post_count": post_count, "footprint_count": footprint_count}


def list_footprint_cafes(user_id):
    """Return cafes where the user has posted at least once."""
    return _cafe_query(
        "WHERE cafes.cafe_id IN (SELECT cafe_id FROM posts WHERE user_id = ?)",
        (user_id, user_id),
        """
        ORDER BY (
            SELECT MAX(posts.created_at) FROM posts
            WHERE posts.cafe_id = cafes.cafe_id AND posts.user_id = ?
        ) DESC
        """,
    )
