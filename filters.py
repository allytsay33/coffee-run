"""Filtering logic for the explore page."""


def filtered_cafes(cafes, keyword, area, minimum_rating, selected_tags):
    """Return cafes that match keyword, area, rating, and tag filters."""
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

        # Keep each condition separate so future teammates can add new filters
        # without touching unrelated logic.
        matches_keyword = not keyword or keyword in searchable
        matches_area = area == "全部" or cafe["area"] == area
        matches_rating = combined_rating >= minimum_rating
        matches_tags = not selected_tags or all(tag in cafe["tags"] for tag in selected_tags)

        if matches_keyword and matches_area and matches_rating and matches_tags:
            results.append(cafe)

    return results
