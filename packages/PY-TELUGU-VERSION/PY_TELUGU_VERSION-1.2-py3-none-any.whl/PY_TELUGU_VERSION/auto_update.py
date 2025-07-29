import sys, time, os, hashlib, json, re, tempfile, shutil, ctypes, platform, subprocess

HERE = os.path.dirname(__file__)
MAP_FILE = os.path.join(HERE, "keywords_te.json")

with open(MAP_FILE, "r", encoding="utf-8") as f:
    ENG_TO_TEL = json.load(f)

TEL_TO_ENG = {tel: eng for eng, tel in ENG_TO_TEL.items()}
_WORD = r"(?<![\w\u0C00-\u0C7F]){0}(?![\w\u0C00-\u0C7F])"

def _generic_replace(code: str, mapping: dict) -> str:
    for k, v in mapping.items():
        code = re.sub(_WORD.format(re.escape(k)), v, code)
    return code

def eng2tel(code: str) -> str: return _generic_replace(code, ENG_TO_TEL)
def tel2eng(code: str) -> str: return _generic_replace(code, TEL_TO_ENG)

def _atomic_write(path: str, new_text: str):
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        tmp.write(new_text)
        tmp.flush()
        os.fsync(tmp.fileno())
    shutil.move(tmp.name, path)
    os.utime(path, None)

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    def _is_pycharm_running():
        try:
            output = subprocess.check_output("tasklist", shell=True, text=True)
            for proc_name in ["pycharm64.exe", "pycharm.exe", "idea64.exe", "idea.exe", "jetbrains.exe"]:
                if proc_name.lower() in output.lower():
                    return True
            return False
        except Exception:
            return False

    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_Y = 0x59
    VK_S = 0x53

    def _send_key_combination(*vk_codes):
        for vk in vk_codes:
            user32.keybd_event(vk, 0, 0, 0)
            time.sleep(0.01)
        for vk in reversed(vk_codes):
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)

    def _send_ctrl_s_then_ctrl_alt_y():
        if _is_pycharm_running():
            _send_key_combination(VK_CONTROL, VK_S)
            time.sleep(0.1)
            _send_key_combination(VK_CONTROL, VK_MENU, VK_Y)

else:
    def _send_ctrl_s_then_ctrl_alt_y():
        print("📣 Please press Ctrl+S and then Ctrl+Alt+Y manually (non-Windows OS)")

def _watch(path: str, interval: float = 1.0):
    print(f"🔄  Watching {path} — Ctrl-C to stop")
    last_hash = None
    while True:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            digest = hashlib.sha256(text.encode()).hexdigest()

            if digest != last_hash:
                new = eng2tel(text)
                if new != text:
                    _atomic_write(path, new)
                    # print("✨ Telugu keywords injected — saving and refreshing editor")
                    time.sleep(0.15)
                    _send_ctrl_s_then_ctrl_alt_y()
                    last_hash = hashlib.sha256(new.encode()).hexdigest()
                else:
                    last_hash = digest

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n⏹️  Watcher stopped")
            break

def main():
    if len(sys.argv) != 2:
        print("Usage: pythontel <file.py>")
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.isfile(target):
        print("File not found:", target)
        sys.exit(1)

    _watch(target)

if __name__ == "__main__":
    main()
