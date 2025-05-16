#!/usr/bin/env python3
import sys

def binary_to_text(binary_string):
    binary_string = binary_string.replace(" ", "").replace("\n", "").replace("\r", "")
    if len(binary_string) % 8 != 0:
        print(f"Cảnh báo: Chuỗi nhị phân không chia hết cho 8 bit, có thể bị cắt hoặc bổ sung.")
    
    text = ""
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            try:
                decimal = int(byte, 2)
                text += chr(decimal)
            except ValueError:
                print(f"Cảnh báo: Byte {byte} không hợp lệ, bỏ qua.")
                continue
        else:
            print(f"Cảnh báo: Byte cuối {byte} không đủ 8 bit, bỏ qua.")
            break
    return text

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Cách dùng: ./binary_to_text.py <tệp_nhị_phân_đầu_vào> [tệp_văn_bản_đầu_ra]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else "text_output.txt"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            binary_string = f.read()
    except IOError as e:
        print(f"Lỗi khi đọc file {input_file}: {e}")
        sys.exit(1)

    text_message = binary_to_text(binary_string)
    print(f"Thông điệp văn bản: {text_message}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text_message)
        print(f"Text has been written to {output_file}")
    except IOError as e:
        print(f"Lỗi khi ghi file {output_file}: {e}")

if __name__ == "__main__":
    main()
