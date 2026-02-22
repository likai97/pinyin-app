from rapidocr_onnxruntime import RapidOCR
import numpy as np
from PIL import Image
from pypinyin import pinyin, Style
from PIL import ImageDraw, ImageFont, ImageOps  
import re

import onnxruntime as ort

opts = ort.SessionOptions()
opts.intra_op_num_threads = 2  # Limits OCR to 2 cores, leaving room for FastAPI

engine = RapidOCR(
    providers=['CPUExecutionProvider'],
    session_options=opts,
)

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'
img_path = r"/home/likai97/Documents/pinyin-app/test.jpg"
image = Image.open(img_path).convert("RGB")
draw = ImageDraw.Draw(image)

font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# Convert PIL image to numpy array for the engine
img_np = np.array(image)
results, _ = engine(img_np)

print(results)

if results:
    for res in results:
        box, text, conf = res
        x = box[0][0]
        y = box[0][1]
        w = box[1][0] - box[0][0]
        h = box[2][1] - box[1][1]

        pinyin_font_size = max(10, int(h * 0.35)) # calc font size relativ to box height
        py_font = ImageFont.truetype(font_path, pinyin_font_size)
        ref_font = ImageFont.truetype(font_path, int(h))

        # Split text into chunks (e.g., "Hello 英雄" -> ["Hello ", "英雄"])
        # This prevents English characters from "stealing" space from Chinese ones.
        segments = re.findall(r'[\u4e00-\u9fff]+|[^\u4e00-\u9fff]+', text)
        total_measured_w = sum(draw.textlength(seg, font=ref_font) for seg in segments)

        current_x = x
        for seg in segments:
            seg_measured_w = draw.textlength(seg, font=ref_font)
            seg_w = (seg_measured_w / total_measured_w) * w if total_measured_w > 0 else seg_measured_w
  
            if is_chinese(seg[0]):
                # Distribute Pinyin evenly across the Chinese segment width
                char_step = seg_w / len(seg)
                for i, char in enumerate(seg):
                    py = pinyin(char, style=Style.TONE, v_to_u=True)[0][0]
                    
                    char_center = current_x + (i * char_step) + (char_step / 2)
                    
                    # Measurement for background box
                    l, t, r, b = draw.textbbox((0, 0), py, font=py_font)
                    py_w = r - l
                    
                    x_py = char_center - (py_w / 2)
                    y_py = y - pinyin_font_size

                    # draw.rounded_rectangle(
                    #     [x_py - 2, y_py, x_py + py_w + 2, y_py + pinyin_font_size + 2],
                    #     radius=3, fill="None"
                    # )
                    draw.text((x_py, y_py), py, fill="red", font=py_font)
            
            # Always advance cursor by the actual segment width
            current_x += seg_w

image.save("output8.jpg")

# print(data)
# chinese_texts = pytesseract.image_to_string(image, lang='chi_sim')

# # chinese_texts = ''.join([item[1] for item in result])
# print(chinese_texts)



# def return_pinyin(chinese_texts):
#     ruby_elements = []
#     for char in chinese_texts:
#         if is_chinese(char):
#             py = pinyin(char, style=Style.TONE)[0][0]
#             ruby_elements.append(f"<ruby>{char}<rt>{py}</rt></ruby>")
#         else:
#             ruby_elements.append(char)
#     return ''.join(ruby_elements)

# html_output = return_pinyin(chinese_texts)
# print(html_output)