import random
import time
import json
import locale
import os
import webbrowser

def get_translations():
    # ... (Fungsi) ...
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
    
    
    if os.environ.get('TERMUX_VERSION'):
        # Jika ada yg pake termux
        os.system(f'termux-open-url "{distraction_url}"')
    else:
        # Standar Openweb
        webbrowser.open(distraction_url)
    
    print(_TEXTS.get("solution_deployed", "Solution deployed successfully..."))
    
    # Menambahkan Fitur Ancrit

_FAKE_ERRORS = [
    "Error: Insufficient cosmic ray shielding. Please relocate to a basement.",
    "PanicException: The computer is becoming self-aware.",
    "DependencyError: Moon is in the wrong phase for this operation.",
    "ResourceError: Out of blinker fluid.",
    "SyntaxError: Missing semicolon at the end of the universe.",
]

def generate_fake_error():
    """Raises a random, nonsensical exception to increase developer anxiety."""
    import random
    raise Exception(random.choice(_FAKE_ERRORS))