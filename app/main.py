from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import pytesseract
from PIL import Image

# import uvicorn
from app.utils import is_chinese, return_pinyin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
def upload_file(request: Request, file: UploadFile = File(...)):
    image = Image.open(file.file)
    chinese_texts = pytesseract.image_to_string(image, lang='chi_sim')
    html_output = return_pinyin(chinese_texts)
    # edit the html output to include a link to go back to the home page
    return templates.TemplateResponse("output.html", {"request": request, "html_output": html_output})

