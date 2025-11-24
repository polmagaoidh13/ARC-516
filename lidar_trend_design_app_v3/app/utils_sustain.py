from shapely.geometry import Polygon, box
from shapely.ops import unary_union

def compute_metrics(boundary: Polygon, items: list):
    area = boundary.area
    footprints = [box(*it["bbox"]) for it in items]
    used = unary_union(footprints) if footprints else None
    used_area = used.area if used else 0.0
    coverage = used_area / area if area > 0 else 0.0
    circulation = max(0.0, 1.0 - coverage)
    def modularity(it):
        minx, miny, maxx, maxy = it["bbox"]
        w = maxx - minx
        d = maxy - miny
        r = max(w, d) / min(w, d)
        return 1.0 if abs(r - 1.0) < 0.2 or abs(r - 2.0) < 0.2 else 0.0
    modular_score = sum(modularity(it) for it in items) / max(1, len(items))
    material_efficiency = 0.6 * (1 - coverage) + 0.4 * modular_score
    return {
        "room_area_m2": round(area, 3),
        "furniture_coverage_ratio": round(coverage, 3),
        "circulation_ratio": round(circulation, 3),
        "modular_reuse_score": round(modular_score, 3),
        "material_efficiency_score": round(material_efficiency, 3)
    }
