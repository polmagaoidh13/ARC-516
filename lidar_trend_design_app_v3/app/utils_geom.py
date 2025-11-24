import numpy as np
from shapely.geometry import MultiPoint, Polygon
from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import open3d as o3d
import numpy as np
import cv2
import os
import uuid

def fit_floor_plane(points: np.ndarray):
    X = points[:, :2]
    y = points[:, 2]
    model = make_pipeline(PolynomialFeatures(1), RANSACRegressor(random_state=0))
    model.fit(X, y)
    a, b = model.named_steps["ransacregressor"].estimator_.coef_[1:3]
    c = model.named_steps["ransacregressor"].estimator_.intercept_
    return np.array([a, b, -1.0, c])

def project_to_plane(points: np.ndarray, plane: np.ndarray, band: float = 0.05):
    a, b, c, d = plane
    num = a*points[:,0] + b*points[:,1] + c*points[:,2] + d
    den = a*a + b*b + c*c
    dist = np.abs(num) / np.sqrt(den)
    floor_mask = dist < band
    floor_pts = points[floor_mask]
    n = np.array([a,b,c])
    proj = floor_pts - np.outer((num[floor_mask]/den), n)
    return proj

def polygon_from_points(xy: np.ndarray) -> Polygon:
    if xy.shape[0] < 3:
        raise ValueError("Not enough points for boundary")
    hull = MultiPoint(xy).convex_hull
    if isinstance(hull, Polygon):
        return hull.buffer(0)
    return hull.envelope.buffer(0)

def render_depth_view(points: np.ndarray, width: int = 768, height: int = 512):
    # Try Open3D offscreen rendering first, then fall back to a simple projection
    try:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        vis = o3d.visualization.rendering.OffscreenRenderer(width, height)
        mat = o3d.visualization.rendering.MaterialRecord()
        mat.shader = "defaultUnlit"
        scene = vis.scene
        scene.add_geometry("room", pcd, mat)
        center = pcd.get_center()
        bb = pcd.get_axis_aligned_bounding_box()
        vis.setup_camera(60.0, bb, center)
        depth = vis.render_to_depth_image(z_in_view_space=True)
        depth_np = np.asarray(depth)
        depth_norm = depth_np.copy()
        depth_norm -= np.nanmin(depth_norm)
        depth_norm /= (np.nanmax(depth_norm)+1e-9)
        depth_u8 = (255*(1.0 - depth_norm)).astype("uint8")
        out_path = f"/tmp/{uuid.uuid4().hex}_depth.png"
        import cv2
        cv2.imwrite(out_path, depth_u8)
        vis.release()
        return out_path
    except Exception:
        # Orthographic projection fallback
        x = points[:,0]; y = points[:,1]; z = points[:,2]
        x_norm = (x - x.min()) / max(1e-6, (x.max()-x.min()))
        y_norm = (y - y.min()) / max(1e-6, (y.max()-y.min()))
        z_norm = (z - z.min()) / max(1e-6, (z.max()-z.min()))
        img = np.ones((height, width), dtype="float32")
        xs = (x_norm * (width-1)).astype("int32")
        ys = (y_norm * (height-1)).astype("int32")
        img[ys, xs] = 1.0 - z_norm
        img = (255 * img).astype("uint8")
        out_path = f"/tmp/{uuid.uuid4().hex}_depth.png"
        import cv2
        cv2.imwrite(out_path, img)
        return out_path
