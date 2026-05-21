from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

import database
import google_maps


UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"
DEFAULT_TAGS = ["安靜", "插座", "不限時", "適合讀書", "適合聊天", "甜點", "平價", "晚上營業", "學生友善"]


def initialize_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "selected_cafe_id" not in st.session_state:
        st.session_state.selected_cafe_id = None
    if "api_key_override" not in st.session_state:
        st.session_state.api_key_override = ""


def current_api_key():
    return google_maps.get_api_key(st.session_state.get("api_key_override"))


def format_distance(distance_meters):
    if not distance_meters:
        return "距離待補"
    if distance_meters >= 1000:
        return f"{distance_meters / 1000:.1f} km"
    return f"{distance_meters} m"


def format_tags(tags):
    return " ".join(f"`{tag}`" for tag in tags if tag)


def save_uploaded_file(uploaded_file, folder):
    if uploaded_file is None:
        return None
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
    filename = f"{folder}_{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / filename
    destination.write_bytes(uploaded_file.getbuffer())
    return str(destination)


def filtered_cafes(cafes, keyword, area, minimum_rating, selected_tags):
    keyword = keyword.strip().lower()
    results = []
    for cafe in cafes:
        combined_rating = cafe["user_rating"] or cafe["rating"]
        searchable = " ".join(
            [
                cafe["name"],
                cafe["area"],
                cafe["address"],
                cafe["description"],
                " ".join(cafe["tags"]),
            ]
        ).lower()
        matches_keyword = not keyword or keyword in searchable
        matches_area = area == "全部" or cafe["area"] == area
        matches_rating = combined_rating >= minimum_rating
        matches_tags = not selected_tags or all(tag in cafe["tags"] for tag in selected_tags)
        if matches_keyword and matches_area and matches_rating and matches_tags:
            results.append(cafe)
    return results


def render_login_page():
    st.title("Coffee Run")
    st.write("請先輸入暱稱進入系統。這是課堂專案用的簡易登入，不會驗證密碼。")
    with st.form("login_form"):
        username = st.text_input("帳號名", placeholder="例如：ally")
        submitted = st.form_submit_button("進入")
        if submitted:
            user = database.get_or_create_user(username)
            if user is None:
                st.warning("請輸入帳號名。")
            else:
                st.session_state.user = user
                st.rerun()


def render_sidebar():
    user = database.get_user(st.session_state.user["user_id"])
    st.session_state.user = user
    stats = database.get_user_stats(user["user_id"])
    st.sidebar.title("Coffee Run")
    st.sidebar.caption(f'@{user["username"]}')
    st.sidebar.metric("貼文數", stats["post_count"])
    st.sidebar.metric("探店數", stats["footprint_count"])
    st.sidebar.metric("收藏", stats["favorite_count"])
    st.sidebar.text_input(
        "Google Maps API Key",
        key="api_key_override",
        type="password",
        help="可留空。留空時會使用本機範例資料與 Streamlit 地圖。",
    )
    if st.sidebar.button("登出"):
        st.session_state.user = None
        st.rerun()
    return st.sidebar.radio("功能", ["探索地圖", "社群", "個人頁", "推薦排行"])


def render_map(cafes):
    map_cafes = [cafe for cafe in cafes if cafe.get("lat") is not None and cafe.get("lng") is not None]
    if not map_cafes:
        st.info("目前沒有可顯示在地圖上的座標資料。")
        return

    api_key = current_api_key()
    static_url = google_maps.static_map_url(map_cafes, api_key)
    if static_url:
        st.image(static_url, caption="Google Static Maps API")
    else:
        st.map(pd.DataFrame([{"lat": cafe["lat"], "lon": cafe["lng"]} for cafe in map_cafes]))


def render_cafe_card(cafe):
    user = st.session_state.user
    favorite_ids = database.get_favorite_ids(user["user_id"])
    is_favorite = cafe["cafe_id"] in favorite_ids
    combined_rating = cafe["user_rating"] or cafe["rating"]

    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.subheader(cafe["name"])
            st.caption(f'{cafe["area"]} | {cafe["address"]}')
            st.write(cafe["description"])
            st.write(format_tags(cafe["tags"]))
        with right:
            st.metric("評分", f"{combined_rating:.1f}")
            st.metric("距離", format_distance(cafe["distance_meters"]))
            if st.button("詳情", key=f'detail_{cafe["cafe_id"]}'):
                st.session_state.selected_cafe_id = cafe["cafe_id"]
            label = "取消收藏" if is_favorite else "收藏"
            if st.button(label, key=f'favorite_{cafe["cafe_id"]}'):
                if is_favorite:
                    database.remove_favorite(user["user_id"], cafe["cafe_id"])
                else:
                    database.add_favorite(user["user_id"], cafe["cafe_id"])
                st.rerun()


def render_cafe_detail():
    cafe_id = st.session_state.selected_cafe_id
    if not cafe_id:
        return
    cafe = database.get_cafe(cafe_id)
    if not cafe:
        return

    st.divider()
    st.header(cafe["name"])
    detail_cols = st.columns([2, 1])
    with detail_cols[0]:
        st.write(cafe["description"])
        st.write(f'地址：{cafe["address"]}')
        if cafe["opening_hours"]:
            st.text(cafe["opening_hours"])
        if cafe["website"]:
            st.link_button("官方網站", cafe["website"])
        if cafe["maps_url"]:
            st.link_button("Google Maps", cafe["maps_url"])
        st.write(format_tags(cafe["tags"]))
    with detail_cols[1]:
        st.metric("Google 評分", f'{cafe["rating"]:.1f}')
        st.metric("使用者評分", f'{cafe["user_rating"]:.1f}' if cafe["user_rating"] else "尚無")
        if cafe["google_place_id"] and current_api_key():
            if st.button("同步 Google 詳情"):
                try:
                    details = google_maps.fetch_place_details(cafe["google_place_id"], current_api_key())
                    updated = dict(cafe)
                    updated.update({key: value for key, value in details.items() if value is not None})
                    database.upsert_cafe(updated)
                    st.success("已同步 Google 詳情")
                    st.rerun()
                except Exception as error:
                    st.error(f"Google 詳情同步失敗：{error}")

    posts = database.list_posts(cafe_id=cafe_id)
    st.subheader("連結此咖啡廳的社群貼文")
    if not posts:
        st.info("目前還沒有貼文。")
    for post in posts:
        render_post_card(post, compact=True)


def render_explore_page():
    st.title("探索地圖")
    st.write("用 Google Places API 搜尋真實咖啡廳，並用使用者貼文補充篩選資料。")

    api_key = current_api_key()
    with st.expander("Google Places 搜尋", expanded=False):
        google_keyword = st.text_input("Google 搜尋關鍵字", value="咖啡廳")
        if st.button("搜尋並加入探索清單"):
            if not api_key:
                st.warning("請先在側邊欄輸入 Google Maps API Key。沒有 key 時可以先使用本機範例資料。")
            else:
                try:
                    cafes = google_maps.search_cafes(google_keyword, api_key)
                    for cafe in cafes:
                        database.upsert_cafe(cafe)
                    st.success(f"已加入 {len(cafes)} 筆 Google Places 搜尋結果")
                    st.rerun()
                except Exception as error:
                    st.error(f"Google Places 搜尋失敗：{error}")

    cafes = database.list_cafes()
    areas = ["全部"] + database.list_areas()
    tags = database.list_all_tags()

    filter_cols = st.columns([2, 1, 1, 2])
    with filter_cols[0]:
        keyword = st.text_input("站內搜尋", placeholder="店名、地區、特色、地址")
    with filter_cols[1]:
        area = st.selectbox("地區", areas)
    with filter_cols[2]:
        minimum_rating = st.slider("最低評分", 0.0, 5.0, 0.0, 0.5)
    with filter_cols[3]:
        selected_tags = st.multiselect("精細篩選", tags, placeholder="安靜、插座、不限時")

    results = filtered_cafes(cafes, keyword, area, minimum_rating, selected_tags)
    st.caption(f"找到 {len(results)} 間咖啡廳")
    render_map(results)

    st.subheader("搜尋結果")
    for cafe in results:
        render_cafe_card(cafe)

    render_cafe_detail()


def render_post_form(cafes):
    st.subheader("發文")
    cafe_options = {f'{cafe["name"]}｜{cafe["area"]}': cafe["cafe_id"] for cafe in cafes}
    with st.form("post_form", clear_on_submit=True):
        cafe_label = st.selectbox("連結咖啡廳", list(cafe_options))
        rating = st.slider("評分", 1, 5, 4)
        tags = st.multiselect("補充篩選標籤", DEFAULT_TAGS)
        content = st.text_area("內文", placeholder="分享這間咖啡廳的環境、餐點、適合情境。")
        image = st.file_uploader("上傳圖片", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("發布貼文")
        if submitted:
            if not content.strip():
                st.warning("請輸入貼文內容。")
            else:
                image_path = save_uploaded_file(image, "post")
                database.create_post(
                    st.session_state.user["user_id"],
                    cafe_options[cafe_label],
                    content,
                    rating,
                    image_path,
                    tags,
                )
                st.success("已發布貼文")
                st.rerun()


def render_post_card(post, compact=False):
    user_id = st.session_state.user["user_id"]
    liked = database.user_liked_post(user_id, post["post_id"])
    with st.container(border=True):
        st.caption(f'{post["cafe_name"]}｜@{post["username"]}｜{post["created_at"]}')
        if post.get("image_path") and Path(post["image_path"]).exists():
            st.image(post["image_path"], use_container_width=True)
        st.write(post["content"])
        st.write(format_tags(post.get("tags", [])))
        cols = st.columns([1, 1, 1, 3])
        cols[0].metric("評分", f'{post["rating"]}/5')
        cols[1].metric("愛心", post["like_count"])
        cols[2].metric("留言", post["comment_count"])
        if cols[3].button("收回愛心" if liked else "按愛心", key=f'like_{post["post_id"]}_{compact}'):
            database.toggle_like(user_id, post["post_id"])
            st.rerun()

        with st.expander("留言"):
            for comment in database.list_comments(post["post_id"]):
                st.caption(f'@{comment["username"]}：{comment["content"]}')
            with st.form(f'comment_form_{post["post_id"]}_{compact}', clear_on_submit=True):
                content = st.text_input("新增留言")
                submitted = st.form_submit_button("送出")
                if submitted and content.strip():
                    database.add_comment(user_id, post["post_id"], content)
                    st.rerun()


def render_social_page():
    st.title("社群")
    cafes = database.list_cafes()
    render_post_form(cafes)
    st.divider()
    st.subheader("最新貼文")
    posts = database.list_posts()
    if not posts:
        st.info("目前還沒有貼文。")
    for post in posts:
        render_post_card(post)


def render_profile_page():
    user = database.get_user(st.session_state.user["user_id"])
    stats = database.get_user_stats(user["user_id"])
    st.title("個人頁")

    top_cols = st.columns([1, 3])
    with top_cols[0]:
        if user.get("avatar_path") and Path(user["avatar_path"]).exists():
            st.image(user["avatar_path"], width=160)
        else:
            st.info("尚未上傳頭貼")
    with top_cols[1]:
        st.subheader(user.get("display_name") or user["username"])
        st.caption(f'@{user["username"]}')
        metric_cols = st.columns(3)
        metric_cols[0].metric("貼文數", stats["post_count"])
        metric_cols[1].metric("探店數", stats["footprint_count"])
        metric_cols[2].metric("收藏", stats["favorite_count"])

    with st.expander("編輯個人資料"):
        with st.form("profile_form"):
            display_name = st.text_input("暱稱", value=user.get("display_name") or user["username"])
            avatar = st.file_uploader("頭貼", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("儲存")
            if submitted:
                avatar_path = save_uploaded_file(avatar, "avatar") if avatar else None
                database.update_user_profile(user["user_id"], display_name, avatar_path)
                st.success("已更新個人資料")
                st.rerun()

    st.subheader("足跡地圖")
    footprints = database.list_footprint_cafes(user["user_id"])
    if footprints:
        render_map(footprints)
        for cafe in footprints:
            st.caption(f'{cafe["name"]}｜{cafe["area"]}')
    else:
        st.info("發文後，該咖啡廳會出現在足跡地圖。")

    st.subheader("收藏清單")
    favorites = database.list_favorite_cafes(user["user_id"])
    if not favorites:
        st.info("目前還沒有收藏咖啡廳。")
    for cafe in favorites:
        render_cafe_card(cafe)

    st.subheader("我的貼文")
    my_posts = [post for post in database.list_posts() if post["user_id"] == user["user_id"]]
    if not my_posts:
        st.info("目前還沒有發文。")
    for post in my_posts:
        render_post_card(post, compact=True)


def render_ranking_page():
    st.title("推薦排行")
    cafes = database.list_cafes()
    ranked = sorted(cafes, key=lambda cafe: cafe["user_rating"] or cafe["rating"], reverse=True)
    for index, cafe in enumerate(ranked, start=1):
        with st.container(border=True):
            st.subheader(f'{index}. {cafe["name"]}')
            st.write(
                f'綜合評分 {(cafe["user_rating"] or cafe["rating"]):.1f}｜'
                f'{cafe["area"]}｜{format_distance(cafe["distance_meters"])}'
            )
            st.write(cafe["description"])
            st.write(format_tags(cafe["tags"]))


def main():
    st.set_page_config(page_title="Coffee Run", page_icon="Coffee", layout="wide")
    database.initialize_database()
    initialize_state()

    if st.session_state.user is None:
        render_login_page()
        return

    page = render_sidebar()
    if page == "探索地圖":
        render_explore_page()
    elif page == "社群":
        render_social_page()
    elif page == "個人頁":
        render_profile_page()
    else:
        render_ranking_page()


if __name__ == "__main__":
    main()
