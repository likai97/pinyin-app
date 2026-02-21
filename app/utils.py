from pypinyin import pinyin, Style

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