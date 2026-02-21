from pypinyin import pinyin, Style
from PIL import ImageDraw, ImageFont
import pytesseract

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'

def return_pinyin(chinese_texts):
    ruby_elements = []
    for char in chinese_texts:
        if is_chinese(char):
            py = pinyin(char, style=Style.TONE)[0][0]
            ruby_elements.append(f"<ruby>{char}<rt>{py}</rt></ruby>")
        else:
            ruby_elements.append(char)
    return ''.join(ruby_elements)

def generate_annotated_image(image, data, font_path):
    draw = ImageDraw.Draw(image)
    for i, txt in enumerate(data['text']):
        clean_txt = txt.strip()
        
        if not clean_txt:
            continue
        
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        pinyin_font_size = max(10, int(h * 0.35)) # floor at 10  
        current_font = ImageFont.truetype(font_path, pinyin_font_size)

        chars_in_block = [c for c in clean_txt if is_chinese(c)]
        
        if chars_in_block:
            char_width = w / len(clean_txt)
            # get list of pinyins
            py_list = pinyin(clean_txt, style=Style.TONE)

            for char_idx, char in enumerate(clean_txt):
                
                if py_list:
                    py = py_list[char_idx][0]

                    # Temp bounding box for centering logic
                    char_center_x = x + (char_idx * char_width) + (char_width / 2)
                    temp_bbox = draw.textbbox((0, 0), py, font=current_font)
                    py_w = temp_bbox[2] - temp_bbox[0]

                    x_py_centered = char_center_x - (py_w / 2)
                    y_py = y - pinyin_font_size

                    # bounding boxes  
                    bbox = draw.textbbox((x_py_centered, y_py), py, font=current_font)

                    # padding
                    pad = max(1, int(h * 0.05))
                    padded_box = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad,bbox[3] + pad)

                    # draw rectangle
                    draw.rectangle(padded_box, fill="white")
                    # draw text
                    draw.text((x_py_centered, y_py), py, fill="red", font=current_font)
    return image