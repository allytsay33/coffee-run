"""Explore-page filter rules for Google and community supplied data."""


def filtered_cafes(
    cafes,
    keyword="",
    area="全部",
    minimum_rating=0.0,
    selected_tags=None,
    quick_filters=None,
    maximum_distance=None,
):
    """Return cafes matching text, map, rating, and structured trait filters."""
    keyword = keyword.strip().lower()
    selected_tags = selected_tags or []
    quick_filters = quick_filters or []
    results = []

    for cafe in cafes:
        combined_rating = cafe["user_rating"] or cafe["rating"]
        tags = cafe.get("tags", [])
        searchable = " ".join(
            [cafe["name"], cafe["area"], cafe["address"], cafe["description"], " ".join(tags)]
        ).lower()
        matches = [
            not keyword or keyword in searchable,
            area == "全部" or cafe["area"] == area,
            combined_rating >= minimum_rating,
            not selected_tags or all(tag in tags for tag in selected_tags),
            maximum_distance is None
            or not cafe.get("distance_meters")
            or cafe["distance_meters"] <= maximum_distance,
        ]

        for label in quick_filters:
            if label == "營業中":
                matches.append(cafe.get("open_now") in (None, 1))
            elif label == "深夜咖啡廳":
                matches.append("深夜咖啡廳" in tags or "晚上營業" in tags or (cafe.get("open_late_score") or 0) >= 0.5)
            elif label == "不限時":
                matches.append("不限時" in tags or (cafe.get("no_time_limit_score") or 0) >= 0.5)
            elif label == "插座多":
                matches.append("插座多" in tags or "插座" in tags or (cafe.get("has_outlets_score") or 0) >= 0.5)

        if all(matches):
            results.append(cafe)
    return results
