#!/usr/bin/env python3
import sys
import pdfplumber
import ast
import unicodedata

# Hằng số toàn cục
T = 1/300

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

def decode_shift(dx, dy, group):
    global T
    # Định nghĩa sai số (tolerance)
    tolerance = T / 10  # Sai số 1/10 của T, có thể điều chỉnh

    # Đọc bảng ánh xạ từ file
    if group == 'Nhóm 1' or group == 'Nhóm 3':
        with open("shift_table_4bit.txt", "r") as f:
            shifts = dict(line.strip().split(": ") for line in f if line.strip())
            shifts = {ast.literal_eval(v): k for k, v in shifts.items()}  # Đảo ngược: (dx, dy) -> bit
    elif group == 'Nhóm 2':
        with open("shift_table_2bit.txt", "r") as f:
            shifts = dict(line.strip().split(": ") for line in f if line.strip())
            shifts = {ast.literal_eval(v): k for k, v in shifts.items()}  # Đảo ngược: (dx, dy) -> bit
    else:
        return None

    # Tìm giá trị trong shifts khớp với dx, dy trong khoảng sai số
    for (shift_dx, shift_dy), bits in shifts.items():
        if (abs(dx - shift_dx) <= tolerance and abs(dy - shift_dy) <= tolerance):
            return bits
    return None

def extract_positions(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        char_positions = []
        for page in pdf.pages:
            chars = page.chars
            i = 0
            while i < len(chars):
                char = chars[i]
                if i + 1 < len(chars) and chars[i + 1]['text'] in TOP_TONES:
                    base_char = char['text']
                    tone_char = chars[i + 1]['text']
                    composed_char = unicodedata.normalize('NFC', base_char + tone_char)
                    char_positions.append({
                        "char": composed_char,
                        "base_char": base_char,
                        "top_tone": tone_char,
                        "base_x": char['x0'],
                        "base_y": char['top'],
                        "tone_x": chars[i + 1]['x0'],
                        "tone_y": chars[i + 1]['top'],
                        "width": char['x1'] - char['x0']
                    })
                    i += 2
                else:
                    char_positions.append({
                        "char": char['text'],
                        "base_char": char['text'],
                        "top_tone": None,
                        "base_x": char['x0'],
                        "base_y": char['top'],
                        "tone_x": None,
                        "tone_y": None,
                        "width": char['x1'] - char['x0']
                    })
                    i += 1
        return char_positions

def find_theoretical_tone_position(pos, marks, top_tone):
    from reportlab.lib.pagesizes import letter
    font_size = 13
    ascent = font_size * 0.8
    extra_height = font_size * 0.2
    page_height = letter[1]
    y_offset = 13 * 0.59

    x_reportlab = pos["base_x"]
    y_reportlab = page_height - pos["base_y"] - y_offset
    width = pos["width"]

    base_center_x = x_reportlab + (width / 2) + width * 0.3
    if top_tone == TONE_SAC:
        tone_x_initial = base_center_x + width * 0.2
    elif top_tone == TONE_HUYEN:
        tone_x_initial = base_center_x
    elif top_tone == TONE_NGA:
        tone_x_initial = base_center_x + width * 0.2
    elif top_tone == TONE_HOI:
        tone_x_initial = base_center_x
    else:
        tone_x_initial = base_center_x + width * 0.4

    has_special_mark = any(mark in SPECIAL_MARKS for mark in marks)
    if has_special_mark:
        y_reportlab_base = y_reportlab
    else:
        if top_tone == TONE_NANG:
            y_reportlab_base = y_reportlab
        else:
            y_reportlab_base = y_reportlab - extra_height

    tone_y_initial = y_reportlab_base
    return tone_x_initial, tone_y_initial

def find_corresponding_position(encoded_pos, original_positions, start_idx):
    tolerance = 5.0
    for i in range(start_idx, len(original_positions)):
        orig_pos = original_positions[i]
        if (encoded_pos["char"] == orig_pos["char"] and
            abs(encoded_pos["base_x"] - orig_pos["base_x"]) < tolerance and
            abs(encoded_pos["base_y"] - orig_pos["base_y"]) < tolerance):
            return i, orig_pos
    return None, None

def decode_positions(original_positions, encoded_positions):
    binary_result = ""
    from reportlab.lib.pagesizes import letter
    page_height = letter[1]
    y_offset = 13 * 0.59
    orig_idx = 0

    for enc_pos in encoded_positions:
        composed_char = unicodedata.normalize('NFC', enc_pos["char"])
        base, marks, top_tones = decompose_text(enc_pos["char"])
        if not base or not top_tones:
            continue
        base = base[0]
        marks = marks[0]
        top_tone = top_tones[0]

        group = 'Nhóm 1' if composed_char in GROUP_1 else 'Nhóm 2' if composed_char in GROUP_2 else 'Nhóm 3' if composed_char in GROUP_3 else None
        if not group or not top_tone:
            continue

        # Tìm vị trí ký tự tương ứng trong file gốc
        idx, orig_pos = find_corresponding_position(enc_pos, original_positions, orig_idx)
        if orig_pos is None:
            continue
        orig_idx = idx + 1

        # Tính vị trí lý thuyết của top_tone trong file gốc
        theoretical_tone_x, theoretical_tone_y = find_theoretical_tone_position(orig_pos, marks, top_tone)

        # Lấy vị trí thực tế của top_tone trong file đã mã hóa
        if enc_pos["tone_x"] is not None:
            enc_tone_x = enc_pos["tone_x"]
            enc_tone_y = page_height - enc_pos["tone_y"] - y_offset
           
            # Tính dịch chuyển
            dx_tone = enc_tone_x - theoretical_tone_x
            dy_tone = enc_tone_y - theoretical_tone_y

            # Kiểm tra xem ký tự có bị dịch chuyển không
            if abs(dx_tone) > T/2 or abs(dy_tone) > T/2:
                bit_tone = decode_shift(dx_tone, dy_tone, group)
                if bit_tone:
                    binary_result += bit_tone
    return binary_result

def main():
    if len(sys.argv) != 4:
        print("Cách dùng: ./decode.py tệp_PDF_gốc tệp_PDF_đã_mã_hóa tệp_đầu_ra")
        sys.exit(1)
    original_pdf = sys.argv[1]
    encoded_pdf = sys.argv[2]
    output_file = sys.argv[3]
    original_positions = extract_positions(original_pdf)
    encoded_positions = extract_positions(encoded_pdf)
    binary_message = decode_positions(original_positions, encoded_positions)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(binary_message)
    print(f"The binary message has been saved to {output_file}")

if __name__ == "__main__":
    main()
