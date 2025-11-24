from shapely.geometry import box

CATALOG = [
    {"name": "Sofa 2 seat", "w": 1.7, "d": 0.9, "tags": ["seating"]},
    {"name": "Table coffee", "w": 1.0, "d": 0.6, "tags": ["table"]},
    {"name": "Dining table", "w": 1.6, "d": 0.9, "tags": ["table"]},
    {"name": "Chair", "w": 0.5, "d": 0.5, "tags": ["seating"]},
    {"name": "Storage unit", "w": 1.0, "d": 0.4, "tags": ["storage"]},
]

def place_rect(boundary, w, d, offset=0.2):
    minx, miny, maxx, maxy = boundary.bounds
    step = 0.2
    x = minx + offset
    while x + w <= maxx - offset:
        y = miny + offset
        while y + d <= maxy - offset:
            rect = box(x, y, x + w, y + d)
            if rect.within(boundary):
                return rect
            y += step
        x += step
    return None

def suggest_layout(boundary):
    placed = []
    for item in CATALOG:
        rect = place_rect(boundary, item["w"], item["d"])
        if rect is None:
            continue
        placed.append({
            "name": item["name"],
            "bbox": list(rect.bounds),
            "position": [rect.centroid.x, rect.centroid.y],
            "rotation": 0.0
        })
    return placed
