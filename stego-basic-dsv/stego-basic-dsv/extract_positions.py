#!/usr/bin/env python3
import sys
import pdfplumber

def extract_y_positions(pdf_file):
    """Trích xuất danh sách các giá trị y (top) từ file PDF."""
    y_positions = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            chars = page.chars
            for char in chars:
                y_positions.append(char['top'])
    print(f"Đã trích xuất {len(y_positions)} giá trị y từ {pdf_file}")
    return y_positions

def main():
    if len(sys.argv) != 3:
        print("Cách dùng: ./extract_y_positions.py tệp_PDF tệp_đầu_ra_txt")
        sys.exit(1)
    pdf_file = sys.argv[1]
    output_txt = sys.argv[2]
    
    # Trích xuất các giá trị y
    y_positions = extract_y_positions(pdf_file)
    
    # Lưu vào file .txt
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(str(y_positions))
    with open("task1.stdout", "w") as f:
        f.write("Y coordinates extracted successfully")
    print(f"Y coordinates extracted successfully")

if __name__ == "__main__":
    main()
