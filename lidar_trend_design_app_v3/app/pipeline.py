import io, os
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from .utils_io import load_point_cloud
from .utils_geom import fit_floor_plane, project_to_plane, polygon_from_points, render_depth_view
from .utils_layout import suggest_layout
from .utils_sustain import compute_metrics

def estimate_boundary(file_bytes: bytes, filename: str):
    points = load_point_cloud(io.BytesIO(file_bytes), filename)
    if points.shape[0] < 500:
        raise ValueError("Point cloud too small for a room")
    plane = fit_floor_plane(points)
    floor_pts = project_to_plane(points, plane, band=0.05)
    boundary_poly = polygon_from_points(floor_pts[:, :2])
    items = suggest_layout(boundary_poly)
    metrics = compute_metrics(boundary_poly, items)
    depth_png = render_depth_view(points)
    boundary = list(np.asarray(boundary_poly.exterior.coords))
    return boundary, items, metrics, depth_png
