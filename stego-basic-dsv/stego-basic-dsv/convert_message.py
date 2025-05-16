#!/usr/bin/env python3

import sys

def text_to_binary(text):
    binary = ''.join(format(ord(char), '08b') for char in text)
    return binary

def main():
    if len(sys.argv) != 3:
        print("Cách dùng: ./convert_message.py thông_điệp tệp_đầu_ra")
        sys.exit(1)
    message = sys.argv[1]
    output_file = sys.argv[2]
    binary_result = text_to_binary(message)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(binary_result)
    print(f"Chuỗi nhị phân đã được ghi vào {output_file}")

if __name__ == "__main__":
    main()

