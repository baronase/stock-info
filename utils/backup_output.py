import os
import shutil


def backup_file(filename, ext):
    output_fn = ".".join([filename, ext])
    backup_folder = "backup"
    backup_number = 1
    while True:
        backup_filename = f"{os.path.join(backup_folder, filename)}_{backup_number}.{ext}"
        if not os.path.exists(backup_filename):
            break
        backup_number += 1

    if os.path.exists(output_fn):
        shutil.move(output_fn, backup_filename)
        print(f"Backed up {output_fn} to {backup_filename}")
    else:
        print(f"No file found to back up at {output_fn}")

# USAGE example:
# backup_file("output", "txt")
