import os
import uuid

import numpy as np
import onnxruntime as ort
from rapidocr_onnxruntime import RapidOCR

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from PIL import Image, ImageOps

from app.utils import is_chinese, return_pinyin, generate_annotated_image

app = FastAPI()
font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

opts = ort.SessionOptions()
opts.intra_op_num_threads = 2
engine = RapidOCR(
    providers=["CPUExecutionProvider"],
    session_options=opts,
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    img_np = np.array(image)
    results, _ = engine(img_np)
    
    # Option 1
    full_text = "".join(text for _, text, _ in results) if results else ""
    html_output = return_pinyin(full_text)

    # Option 2
    annotated_img = generate_annotated_image(image.copy(), results, font_path)

    unique_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    annotated_img.save(file_path)

    # edit the html output to include a link to go back to the home page
    return templates.TemplateResponse("output.html", {
        "request": request,
        "html_output": html_output,
        "annotated_url": f"/static/uploads/{unique_name}"
    })

