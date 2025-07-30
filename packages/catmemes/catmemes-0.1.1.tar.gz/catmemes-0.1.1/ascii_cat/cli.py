import json
import os
import sys

from .scraper import scrape_all

MONA_ORIGIN = r"""
            ／￣￣￣￣￣￣＼
            |   You guys   |
     ∩__∩   |   have too   |
   ( ´ー`) <   much spare  |
   (     )  |    time.     |
    | | |   |              |
   (__)__)  ＼＿＿＿＿＿＿／
"""

CAT_FILE = os.path.join(os.path.dirname(__file__), 'cats.json')


def load_cats():
    with open(CAT_FILE, encoding='utf-8') as f:
        return json.load(f)


def main() -> None:
    if len(sys.argv) == 1:
        print(MONA_ORIGIN)
        return

    if sys.argv[1] == 'update':
        scrape_all(output_file=CAT_FILE)
        return

    if os.path.exists(CAT_FILE):
        cats = load_cats()
    else:
        print('Cat file not found. Try `ascii-cat update`.')
        return

    if sys.argv[1] == 'list':
        print('Available cats:', ', '.join(sorted(cats.keys())))
        return

    cat_name = ' '.join(arg for arg in sys.argv[1:]).strip()

    if cat_name in cats:
        print(cats[cat_name])
    else:
        matches = [k for k in cats if cat_name.lower() in k.lower()]  # fuzzy matach
        if matches:
            print(cats[matches[0]])
        else:
            print('Cat name not found. Try `ascii-cat list`.')
