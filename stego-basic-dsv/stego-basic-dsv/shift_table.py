#!/usr/bin/env python3
import sys

def create_shift_table(T):
    # Bảng cho Nhóm 1/3 (4 bit)
    shifts_4bit = {
       
    }
    # Bảng cho Nhóm 2 (2 bit)
    shifts_2bit = {
       
    }
    return shifts_4bit, shifts_2bit

def main():
    if len(sys.argv) != 2:
        print("Cách dùng: ./shift_table.py T")
        sys.exit(1)
    T = float(sys.argv[1])
    shift_table_4bit, shift_table_2bit = create_shift_table(T)
    
    # Ghi bảng 4 bit vào file
    with open("shift_table_4bit.txt", "w") as f:
        for bit, (dx, dy) in shift_table_4bit.items():
            f.write(f"{bit}: ({dx}, {dy})\n")
    
    # Ghi bảng 2 bit vào file
    with open("shift_table_2bit.txt", "w") as f:
        for bit, (dx, dy) in shift_table_2bit.items():
            f.write(f"{bit}: ({dx}, {dy})\n")
    
    with open("task2.stdout", "w") as f:
        f.write("Shift table created successfully")
    print("Shift table created successfully")

if __name__ == "__main__":
    main()
