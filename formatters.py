"""Small formatting helpers used by multiple UI modules."""


def format_distance(distance_meters):
    """Return a human-readable distance label for cafe cards."""
    if not distance_meters:
        return "距離待補"
    if distance_meters >= 1000:
        return f"{distance_meters / 1000:.1f} km"
    return f"{distance_meters} m"


def format_tags(tags):
    """Render cafe or post tags as Streamlit-friendly inline code chips."""
    return " ".join(f"`{tag}`" for tag in tags if tag)
