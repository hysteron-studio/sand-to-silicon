"""Contact sheet: python contact.py [--cols=C] OUTNAME N1 N2 ... (plates by master number, from previews/)."""
import sys, os, json
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'piece_names.json')))
args = sys.argv[1:]
cols = None
if args and args[0].startswith('--cols='): cols = int(args.pop(0).split('=')[1])
name = args[0]; ns = [int(a) for a in args[1:]]
cols = cols or (6 if len(ns) > 12 else 4)
rows = (len(ns) + cols - 1) // cols
t, g = 460, 34
sheet = Image.new('RGB', (cols * t + (cols + 1) * g, rows * t + (rows + 1) * g), (226, 220, 206))
for i, n in enumerate(ns):
    stem = NAMES[str(n)]
    path = f'{ROOT}/previews/{stem}.jpg'
    if not os.path.exists(path):
        path = f'{ROOT}/previews/{stem}.png'
    im = Image.open(path).resize((t, t), Image.LANCZOS)
    sheet.paste(im, (g + (i % cols) * (t + g), g + (i // cols) * (t + g)))
sheet.save(f'{ROOT}/previews/{name}.png')
print(sheet.size)
