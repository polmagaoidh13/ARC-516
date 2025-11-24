import os, uuid
import subprocess
import sys
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from app.pipeline import estimate_boundary
from app.trends import TrendEngine
from app.render import DepthStylizer
from app.learn import FeedbackStore

# Setup project directories
HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, "Desktop", "lidar_trend_design_app")
os.makedirs(os.path.join(ROOT, "app"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "static"), exist_ok=True)

def W(rel, txt):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)

# Create files
W("static/viewer.html", """<!doctype html><html><head><meta charset="utf-8"/>
<title>LiDAR Interior Viewer</title><style>body{font-family:system-ui;margin:24px}img{max-width:90vw}</style></head>
<body><h1>LiDAR Interior Viewer</h1>
<input id="path" placeholder="/tmp/your_image.png" style="width:480px;padding:8px"/><button onclick="view()">View</button>
<img id="img"/><script>function view(){const p=document.getElementById('path').value;
document.getElementById('img').src='/file?path='+encodeURIComponent(p);}</script></body></html>""")

W("app/main.py", r'''from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from app.pipeline import estimate_boundary
from app.trends import TrendEngine
from app.render import DepthStylizer
from app.learn import FeedbackStore
import uuid, os

app = FastAPI(title="LiDAR Trend Aware Interior Generator")

trend_engine = TrendEngine()
stylizer = DepthStylizer()
feedback = FeedbackStore()

class RenderResponse(BaseModel):
    image_path: str
    boundary: list
    items: list
    metrics: dict
    style_prompt: str

@app.post("/render", response_model=RenderResponse)
async def render_space(file: UploadFile = File(...), purpose: str = Form("living room")):
    data = await file.read()
    boundary, items, metrics, depth_png = estimate_boundary(data, file.filename)
    styles = trend_engine.get_style_prompt(purpose)
    out_path = os.path.join("/tmp", f"{uuid.uuid4().hex}_styled.png")
    img_path = stylizer.stylize_with_depth(depth_png, styles, out_path)
    return JSONResponse({"image_path": img_path, "boundary": boundary, "items": items,
                         "metrics": metrics, "style_prompt": styles})

@app.post("/feedback")
async def feedback_endpoint(purpose: str = Form(...), style_prompt: str = Form(...), liked: bool = Form(...)):
    feedback.record(purpose, style_prompt, liked)
    trend_engine.learn_from_feedback(purpose, style_prompt, liked)
    return {"ok": True}

@app.post("/trends/refresh")
async def refresh_trends():
    trend_engine.refresh(limit=100)
    return {"ok": True, "count": len(trend_engine.cache.get("styles", []))}

@app.get("/file")
def file(path: str):
    return FileResponse(path)

@app.get("/viewer", response_class=HTMLResponse)
async def viewer():
    html = open("static/viewer.html", "r", encoding="utf-8").read()
    return HTMLResponse(html)
''')

# Additional files for pipeline, render, etc.
W("app/pipeline.py", r'''import io, numpy as np
from shapely.geometry import Polygon
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
''')

# Install required packages
pkgs = ["fastapi", "uvicorn", "numpy", "shapely", "open3d>=0.18.0", "laspy", "pydantic", "pillow", "opencv-python", "feedparser", "scikit-learn"]
subprocess.check_call([sys.executable, "-m", "pip", "install", *pkgs])

print("Project created at:", ROOT)

# Running the FastAPI server
import uvicorn
uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
