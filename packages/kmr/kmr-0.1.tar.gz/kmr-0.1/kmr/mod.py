def add_print_to_gd(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    lines.insert(0, 'print("Mod aktif!")\n')
    with open(file_path, "w") as f:
        f.writelines(lines)
