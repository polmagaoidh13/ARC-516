from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from app.pipeline import estimate_boundary
from app.trends import TrendEngine
from app.render import DepthStylizer
from app.learn import FeedbackStore
import uuid

app = FastAPI(title="LiDAR Trend Aware Interior Generator v3")

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
    out_path = f"/tmp/{uuid.uuid4().hex}_styled.png"
    img_path = stylizer.stylize_with_depth(depth_png, styles, out_path)
    return JSONResponse({
        "image_path": img_path,
        "boundary": boundary,
        "items": items,
        "metrics": metrics,
        "style_prompt": styles
    })

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
    html = open("static/viewer.html", "r").read()
    return HTMLResponse(html)
