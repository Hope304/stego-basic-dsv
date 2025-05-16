#!/usr/bin/env python3
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import unicodedata
import pdfplumber
import ast  # Để đọc danh sách từ file .txt

# Hằng số toàn cục
T = 1/300

try:
    pdfmetrics.registerFont(TTFont('TimesNewRoman', '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf'))
except:
    print("Font Times New Roman không khả dụng, sử dụng font mặc định Times-Roman.")
    FONT_NAME = "Times-Roman"
else:
    FONT_NAME = "TimesNewRoman"

GROUP_1 = {'à', 'ả', 'ã', 'á', 'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'è', 'ẻ', 'ẽ', 'é', 'ê', 'ề', 'ế', 'ể', 'ễ',
           'ì', 'ỉ', 'ĩ', 'í', 'ò', 'ỏ', 'õ', 'ó', 'ô', 'ồ', 'ố', 'ổ', 'ỗ','ờ','ớ','ở','ỡ','Ớ','Ờ','Ở','Ỡ', 'ù', 'ủ', 'ũ', 'ú',
           'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ỳ', 'ỷ', 'ỹ', 'ý', 'À', 'Ả', 'Ã', 'Á', 'Â', 'È', 'Ẻ', 'Ẽ', 'É',
           'Ê', 'Ì', 'Ỉ', 'Ĩ', 'Í', 'Ò', 'Ỏ', 'Õ', 'Ó', 'Ô', 'Ù', 'Ủ', 'Ũ', 'Ú', 'Ư', 'Ỳ', 'Ỷ', 'Ỹ', 'Ý'}
GROUP_2 = {'ạ', 'ọ', 'ợ', 'ụ', 'ự', 'ỵ', 'ẹ', 'Ắ', 'Ấ', 'Ề', 'Ồ', 'Ẳ', 'Ẩ', 'Ế', 'Ố', 'Ằ', 'Ầ', 'Ể', 'Ổ',
           'Ẵ', 'Ẫ', 'Ễ', 'Ỗ', 'Ạ', 'Ẹ', 'Ụ', 'Ự', 'Ọ', 'Ợ', 'Ỵ'}
GROUP_3 = {'ậ', 'ệ', 'ộ', 'ặ', 'Ặ', 'Ệ', 'Ộ', 'Ậ'}
COMBINING_TONES = {'\u0301', '\u0300', '\u0309', '\u0303', '\u0323', '\u0302', '\u0306'}
TOP_TONES = {'\u0301', '\u0300', '\u0309', '\u0303', '\u0323'}
SPECIAL_MARKS = {'\u0302', '\u0306'}

TONE_SAC = '\u0301'
TONE_HUYEN = '\u0300'
TONE_HOI = '\u0309'
TONE_NGA = '\u0303'
TONE_NANG = '\u0323'

def is_upper_latin(char):
    return char.isalpha() and char.isupper()

def decompose_text(text):
    normalized = unicodedata.normalize('NFD', text)
    base_chars = []
    marks = []
    top_tones = []
    i = 0
    while i < len(normalized):
        char = normalized[i]
        if not unicodedata.combining(char):
            base_char = char
            current_marks = []
            j = i + 1
            while j < len(normalized) and unicodedata.combining(normalized[j]):
                current_marks.append(normalized[j])
                j += 1
            base_chars.append(base_char)
            marks.append(current_marks)
            top_tone = next((mark for mark in current_marks if mark in TOP_TONES), None)
            top_tones.append(top_tone)
        i = j if j > i else i + 1
    return base_chars, marks, top_tones

def encode_special(top_tone, marks, bit_pair, group):
    global T
    if group == 'Nhóm 1' or group == 'Nhóm 3':
        with open("shift_table_4bit.txt", "r") as f:
            shifts = dict(line.strip().split(": ") for line in f if line.strip())
            shifts = {k: ast.literal_eval(v) for k, v in shifts.items()}
        return shifts.get(bit_pair, (0, 0)), 4
    elif group == 'Nhóm 2':
        with open("shift_table_2bit.txt", "r") as f:
            shifts = dict(line.strip().split(": ") for line in f if line.strip())
            shifts = {k: ast.literal_eval(v) for k, v in shifts.items()}
        return shifts.get(bit_pair[:2], (0, 0)), 2
    return (0, 0), 0

def encode_message(base_chars, marks, top_tones, binary):
    result = []
    binary_index = 0
    bits_hidden = 0
    for idx, (base, mark_list, top_tone) in enumerate(zip(base_chars, marks, top_tones)):
        composed_char = unicodedata.normalize('NFC', base + ''.join(mark_list if mark_list else ''))
        group = 'Nhóm 1' if composed_char in GROUP_1 else 'Nhóm 2' if composed_char in GROUP_2 else 'Nhóm 3' if composed_char in GROUP_3 else None

        bit_length = 4 if group == 'Nhóm 1' else 2 if group == 'Nhóm 2' else 6 if group == 'Nhóm 3' else 0

        if binary_index + bit_length > len(binary):
            result.append((base, mark_list, top_tone, (None, None), 0))
            continue

        bit_pair = binary[binary_index:binary_index+bit_length]
        if group == 'Nhóm 1' and top_tone:
            shift, bits = encode_special(top_tone, mark_list, bit_pair, group)
            print(f"Giấu tại vị trí {idx}: Ký tự '{composed_char}', Bit: {bit_pair}, Shift: {shift}")
        elif group == 'Nhóm 2' and top_tone:
            shift, bits = encode_special(top_tone, mark_list, bit_pair, group)
            print(f"Giấu tại vị trí {idx}: Ký tự '{composed_char}', Bit: {bit_pair}, Shift: {shift}")
        elif group == 'Nhóm 3' and top_tone:
            shift, bits = encode_special(top_tone, mark_list, bit_pair, group)
            print(f"Giấu tại vị trí {idx}: Ký tự '{composed_char}', Bit: {bit_pair}, Shift: {shift}")
        else:
            shift = (None, None)
            bits = 0

        result.append((base, mark_list, top_tone, shift, bits))
        binary_index += bits
        bits_hidden += bits

    if bits_hidden < len(binary):
        raise ValueError("Văn bản đầu vào không đủ ký tự đặc biệt để giấu toàn bộ thông điệp.")
    return result, bits_hidden

def extract_original_positions(original_pdf):
    with pdfplumber.open(original_pdf) as pdf:
        char_positions = []
        for page in pdf.pages:
            chars = page.chars
            for char in chars:
                char_positions.append({
                    "char": char['text'],
                    "x": char['x0'],
                    "y": char['top'],
                    "width": char['x1'] - char['x0']
                })
        return char_positions

def create_pdf(original_positions, output_file, text_with_shifts, y_positions):
    c = canvas.Canvas(output_file, pagesize=letter)
    c.setFont(FONT_NAME, 13)
    page_height = letter[1]
    leading = c._leading
    y_offset = 13 * 0.59
    font_size = 13
    ascent = font_size * 0.8
    extra_height = font_size * 0.2

    if len(original_positions) != len(text_with_shifts):
        print(f"Cảnh báo: Số lượng ký tự không khớp! original_positions: {len(original_positions)}, text_with_shifts: {len(text_with_shifts)}")

    if len(original_positions) != len(y_positions):
        sys.exit(1)

    for pos_idx in range(min(len(original_positions), len(text_with_shifts))):
        base, mark_list, top_tone, shift, bits = text_with_shifts[pos_idx]
        composed_char = unicodedata.normalize('NFC', base + ''.join(mark_list if mark_list else ''))

        pos = original_positions[pos_idx]
        x_reportlab = pos["x"]
        y_reportlab = page_height - y_positions[pos_idx] - 2.52429 - y_offset
        width = pos["width"]

        if shift == (None, None):
            c.drawString(x_reportlab, y_reportlab, composed_char)
        else:
            char_without_tone = unicodedata.normalize('NFC', base + ''.join(mark for mark in mark_list if mark != top_tone))
            c.drawString(x_reportlab, y_reportlab, char_without_tone)

            if top_tone and shift != (None, None):
                tone_width = c.stringWidth(top_tone, FONT_NAME, font_size)
                if tone_width == 0:
                    tone_width = font_size * 0.3

                base_center_x = x_reportlab + (width / 2) + width * 0.3
                if top_tone == TONE_SAC:
                    tone_x_initial = base_center_x + width * 0.2
                    top_x_reportlab = tone_x_initial
                elif top_tone == TONE_HUYEN:
                    tone_x_initial = base_center_x
                    top_x_reportlab = tone_x_initial
                elif top_tone == TONE_NGA:
                    tone_x_initial = base_center_x + width * 0.2
                    top_x_reportlab = tone_x_initial
                elif top_tone == TONE_HOI:
                    tone_x_initial = base_center_x
                    top_x_reportlab = tone_x_initial
                else:
                    tone_x_initial = base_center_x + width * 0.4
                    top_x_reportlab = tone_x_initial

                has_special_mark = any(mark in SPECIAL_MARKS for mark in mark_list)
                if has_special_mark:
                    y_reportlab_base = y_reportlab
                else:
                    if top_tone == TONE_NANG:
                        y_reportlab_base = y_reportlab
                    else:
                        y_reportlab_base = y_reportlab - extra_height

                tone_y_initial = y_reportlab_base
                dx, dy = shift
                top_x_reportlab += dx
                top_y_reportlab = y_reportlab_base + dy

                c.drawString(top_x_reportlab, top_y_reportlab, top_tone)

    for pos_idx in range(len(original_positions)):
        if pos_idx >= len(text_with_shifts):
            pos = original_positions[pos_idx]
            x_reportlab = pos["x"]
            y_reportlab = page_height - y_positions[pos_idx] - y_offset
            c.drawString(x_reportlab, y_reportlab, pos["char"])

    c.save()

def main():
    if len(sys.argv) != 5:
        print("Cách dùng: ./encode.py tệp_PDF_gốc tệp_nhị_phân tệp_đầu_ra tệp_y_positions_txt")
        sys.exit(1)
    original_pdf = sys.argv[1]
    binary_file = sys.argv[2]
    output_file = sys.argv[3]
    y_positions_file = sys.argv[4]

    # Đọc các giá trị y từ file y_positions.txt
    with open(y_positions_file, 'r', encoding='utf-8') as f:
        y_positions = ast.literal_eval(f.read())

    original_positions = extract_original_positions(original_pdf)

    text = ""
    for pos in original_positions:
        text += pos["char"]

    with open(binary_file, 'r', encoding='utf-8') as f:
        binary = f.read().strip()

    try:
        base_chars, marks, top_tones = decompose_text(text)
        text_with_shifts, bits_hidden = encode_message(base_chars, marks, top_tones, binary)
        print(f"Đã giấu {bits_hidden} bit vào văn bản.")
    except ValueError as e:
        sys.exit(1)

    create_pdf(original_positions, output_file, text_with_shifts, y_positions)
    print(f"The PDF has been redrawn and saved {output_file}")

if __name__ == "__main__":
    main()
