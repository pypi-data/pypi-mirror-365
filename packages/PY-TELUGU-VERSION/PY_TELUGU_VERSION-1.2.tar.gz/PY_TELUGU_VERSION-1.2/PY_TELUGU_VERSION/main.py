import sys
from PY_TELUGU_VERSION.auto_update import tel2eng
import os
def run_telugu_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        telugu_src = f.read()

    python_src = tel2eng(telugu_src)
    exec(python_src, globals())

def main():
    if len(sys.argv) != 2:
        print("Usage: pythonrun <file.py>")
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    run_telugu_file(file_path)
if __name__ == "__main__":
    main()
