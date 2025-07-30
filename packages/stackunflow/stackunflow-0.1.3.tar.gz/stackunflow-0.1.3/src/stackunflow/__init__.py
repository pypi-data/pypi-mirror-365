import random
import time
import json
import locale
import os
import webbrowser # <-- Kita butuh ini lagi

def get_translations():
    # ... (Fungsi ini tidak perlu diubah) ...
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

_TEXTS = get_translations()
_DISTRACTIONS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.tiktok.com/",
    "https://www.instagram.com/",
    "https://twitter.com/home",
]

def solve(problem_description: str):
    """
    Analyzes your complex coding problem and provides the best possible solution.
    """
    print(_TEXTS.get("analyzing_problem", "Analyzing complex problem..."))
    time.sleep(1)
    print(_TEXTS.get("finding_distraction", "Finding optimal distraction..."))
    time.sleep(1)
    
    distraction_url = random.choice(_DISTRACTIONS)
    
    # --- LOGIKA CERDAS UNTUK MEMILIH CARA MEMBUKA URL ---
    # Cek apakah kita sedang berjalan di dalam lingkungan Termux
    if os.environ.get('TERMUX_VERSION'):
        # Jika ya, gunakan perintah khusus Termux
        os.system(f'termux-open-url "{distraction_url}"')
    else:
        # Jika tidak, gunakan cara standar yang bekerja di semua sistem
        webbrowser.open(distraction_url)
    
    print(_TEXTS.get("solution_deployed", "Solution deployed successfully..."))