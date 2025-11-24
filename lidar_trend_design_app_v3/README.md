# LiDAR Trend Aware Interior Generator v3

This guide walks you from zero to a running prototype that
1) reads a LiDAR scan and extracts room size and boundary
2) keeps a lightweight self learning store of style cues from design feeds
3) generates a styled image using depth guidance that respects the scanned geometry
4) records user feedback to bias future styles

## Install
1. Install Python 3.10 or newer
2. pip install -r requirements.txt

## Run the API
uvicorn app.main:app --reload

## Test in three steps
1. Upload a PLY or LAS to /render along with a purpose string such as living room
2. Open /viewer in your browser and paste the returned image path to preview
3. POST to /feedback with purpose, style_prompt, liked=true or false to teach the system

## Endpoints
POST /render -> returns image path, boundary, items, metrics, style_prompt
POST /feedback -> record if you liked a result to bias future prompts
POST /trends/refresh -> refresh the style database from feeds
GET  /viewer -> simple web viewer
GET  /file?path=... -> serve a generated file

## Notes
The depth guided image generator uses a ControlNet SDXL model if available
If your environment cannot load it the app will create a placeholder image so you can still test the loop

## Research alignment
It computes quick material efficiency proxies and leaves clear hooks to connect EPD data and circularity modules
