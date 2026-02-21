import os
import uuid

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import pytesseract
from PIL import Image, ImageOps

# import uvicorn
from app.utils import is_chinese, return_pinyin, generate_annotated_image

app = FastAPI()
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    image = Image.open(file.file)
    
    # Option 1
    chinese_texts = pytesseract.image_to_string(image, lang='chi_sim')
    html_output = return_pinyin(chinese_texts)

    # Option 2
    image_greyscale = image.convert('L') 
    image_greyscale = ImageOps.autocontrast(image.convert('L')) # increase contrast
    custom_config = r'--oem 3 --psm 3'
    ocr_data = pytesseract.image_to_data(
        image_greyscale,
        lang='chi_sim', 
        config=custom_config,
        output_type=pytesseract.Output.DICT
    )
    annotated_img = generate_annotated_image(image.copy(), ocr_data, font_path)

    unique_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    annotated_img.save(file_path)

    # edit the html output to include a link to go back to the home page
    return templates.TemplateResponse("output.html", {
        "request": request,
        "html_output": html_output,
        "annotated_url": f"/static/uploads/{unique_name}"
    })

