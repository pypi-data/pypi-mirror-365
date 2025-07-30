import random
import time
import json
import locale
import os
import webbrowser
import functools

# Coba impor tomli, library untuk membaca file .toml
try:
    import tomli
except ImportError:
    tomli = None

# --- PENGATURAN DEFAULT ---
_DEFAULT_CONFIG = {
    "distractions": [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.tiktok.com/",
        "https://www.instagram.com/",
        "https://twitter.com/home",
    ],
    "fake_errors": [
        "Error: Insufficient cosmic ray shielding. Please relocate to a basement.",
        "PanicException: The computer is becoming self-aware.",
        "DependencyError: Moon is in the wrong phase for this operation.",
        "ResourceError: Out of blinker fluid.",
        "SyntaxError: Missing semicolon at the end of the universe.",
    ]
}

def _load_config():
    """Mencari dan memuat file .stackunflow.toml dari direktori saat ini."""
    config = _DEFAULT_CONFIG.copy()
    if tomli:
        try:
            with open(".stackunflow.toml", "rb") as f:
                user_config = tomli.load(f)
                if "distractions" in user_config:
                    config["distractions"] = user_config["distractions"]
                if "fake_errors" in user_config:
                    config["fake_errors"] = user_config["fake_errors"]
        except FileNotFoundError:
            pass
    return config

def get_translations():
    """Mendeteksi bahasa sistem dan memuat file terjemahan yang sesuai."""
    try:
        lang_code, _ = locale.getdefaultlocale()
        lang_code = lang_code.split('_')[0]
    except Exception:
        lang_code = 'en'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(base_dir, 'locales')
    lang_file_path = os.path.join(locales_dir, f"{lang_code}.json")
    if not os.path.exists(lang_file_path):
        lang_file_path = os.path.join(locales_dir, 'en.json')
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- MUAT KONFIGURASI & TERJEMAHAN SAAT PAKET DIIMPOR ---
_CONFIG = _load_config()
_TEXTS = get_translations()


# --- FUNGSI-FUNGSI PUBLIK ---

def solve(problem_description: str):
    """Membuka situs distraksi dari daftar konfigurasi."""
    print(_TEXTS.get("analyzing_problem", "Analyzing complex problem..."))
    time.sleep(1)
    
    distraction_url = random.choice(_CONFIG["distractions"])
    
    if os.environ.get('TERMUX_VERSION'):
        os.system(f'termux-open-url "{distraction_url}"')
    else:
        webbrowser.open(distraction_url)
    
    print(_TEXTS.get("solution_deployed", "Solution deployed successfully..."))

def generate_fake_error():
    """Melempar error palsu dari daftar konfigurasi."""
    raise Exception(random.choice(_CONFIG["fake_errors"]))

def add_bug(file_path: str):
    """Menambahkan fitur tak terduga (bug) ke file yang ditentukan."""
    print(f"⚠️ WARNING: This function will modify '{file_path}' directly.")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print("File is empty. Nothing to do.")
            return

        sabotage_functions = [
            _sabotage_comment_out_line,
            _sabotage_duplicate_line,
            _sabotage_swap_true_false
        ]
        sabotage_to_apply = random.choice(sabotage_functions)
        
        modified_lines = sabotage_to_apply(lines)
        
        with open(file_path, 'w') as f:
            f.writelines(modified_lines)
            
        print(f"✅ 'Optimization' successfully applied to {file_path}. Good luck.")

    except FileNotFoundError:
        print(f"❌ ERROR: File not found at '{file_path}'.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# --- FUNGSI INTERNAL (HELPER) ---

def _sabotage_comment_out_line(lines):
    line_index = random.randint(0, len(lines) - 1)
    if lines[line_index].strip():
        lines[line_index] = "#" + lines[line_index]
    return lines

def _sabotage_duplicate_line(lines):
    line_index = random.randint(0, len(lines) - 1)
    if lines[line_index].strip():
        lines.insert(line_index, lines[line_index])
    return lines
    
def _sabotage_swap_true_false(lines):
    for i, line in enumerate(lines):
        if "True" in line:
            lines[i] = line.replace("True", "False", 1)
            break
        elif "False" in line:
            lines[i] = line.replace("False", "True", 1)
            break
    return lines