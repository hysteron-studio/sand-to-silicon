# Sand to Silicon

**41 plates by HYSTERON** - an anonymous code artist.

*Sand to Silicon* follows the journey of a chip from raw quartz ore to a working
intelligence: ore, reduction, purification, crystal growth, polishing, lithography,
etching, implant, packaging, test, servers and finally a tiny transformer reading
"from matter to mind". Each plate is a technical drawing of one real manufacturing step,
built from published engineering figures (cited inside each script's `DATA` block).

## Method

Every image is 100% code: Python, NumPy, SciPy and Pillow. No AI image tools,
no photos, no hand drawing.

- `gen/style.py` - the shared toolkit: a 3000x3000 supersampled canvas with two
  layers (ink and accent), hatching and line tools, a paper texture, ink bleed and
  dry-brush finishing, and a 41-step accent palette interpolated in CIELAB.
- `gen/pNN_*.py` - one generator per plate. Real process numbers (temperatures,
  pitches, layer counts, yields) drive the geometry.
- `gen/contact.py` - builds a contact sheet from the previews.
- `gen/titles.json` - plate titles.

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cd gen
python p01_ore.py          # writes ../images/01.png, ../previews/01.png, ../data/01.json
python contact.py sheet 1 2 3 4
```

## Seeds are private

Every random choice comes from a seeded generator, but the seeds used for the
originals are **not published** (`SEED = None  # private, not published`). Running the code
gives you a new variation of each plate every time - never the exact original.
That keeps the minted originals unique.

## Previews

`previews/` holds small 480 px JPEG previews of the 41 originals.

## Collection

- Rarible: <RARIBLE_COLLECTION_URL>
- Wallet: <HYSTERON_WALLET_ADDRESS>

## License

- **Code** (`gen/`, `requirements.txt`): MIT - see `LICENSE`.
- **Artwork** (the images in `previews/` and the original plates): CC BY-NC 4.0 -
  see `LICENSE-ART`. Share with credit to HYSTERON, non-commercial use only.
  Owning the code does not grant rights to the original artworks.
