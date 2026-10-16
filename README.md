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
- `gen/HYSTERON.SandToSilicon.NN.of.41.PieceName.py` - one generator per plate.
  Real process numbers (temperatures, pitches, layer counts, yields) drive the geometry.
- `gen/contact.py` - builds a contact sheet from the previews.
- `gen/titles.json` / `gen/piece_names.json` - plate titles and file stems.

## Pieces

- `HYSTERON.SandToSilicon.01.of.41.TheOre` — The Ore
- `HYSTERON.SandToSilicon.02.of.41.TheReduction` — The Reduction
- `HYSTERON.SandToSilicon.03.of.41.ThePurification` — The Purification
- `HYSTERON.SandToSilicon.04.of.41.TheCrystal` — The Crystal
- `HYSTERON.SandToSilicon.05.of.41.ThePolish` — The Polish
- `HYSTERON.SandToSilicon.06.of.41.TheArchitecture` — The Architecture
- `HYSTERON.SandToSilicon.07.of.41.TheBlueprint` — The Blueprint
- `HYSTERON.SandToSilicon.08.of.41.TheBlank` — The Blank
- `HYSTERON.SandToSilicon.09.of.41.TheWriter` — The Writer
- `HYSTERON.SandToSilicon.10.of.41.TheShield` — The Shield
- `HYSTERON.SandToSilicon.11.of.41.TheResist` — The Resist
- `HYSTERON.SandToSilicon.12.of.41.TheCoatAndDevelop` — The Coat & Develop
- `HYSTERON.SandToSilicon.13.of.41.TheLight` — The Light
- `HYSTERON.SandToSilicon.14.of.41.TheFilm` — The Film
- `HYSTERON.SandToSilicon.15.of.41.TheSpecialistFilm` — The Specialist Film
- `HYSTERON.SandToSilicon.16.of.41.TheEtch` — The Etch
- `HYSTERON.SandToSilicon.17.of.41.TheGas` — The Gas
- `HYSTERON.SandToSilicon.18.of.41.TheFlow` — The Flow
- `HYSTERON.SandToSilicon.19.of.41.TheImplant` — The Implant
- `HYSTERON.SandToSilicon.20.of.41.TheClean` — The Clean
- `HYSTERON.SandToSilicon.21.of.41.ThePlanarize` — The Planarize
- `HYSTERON.SandToSilicon.22.of.41.TheInspect` — The Inspect
- `HYSTERON.SandToSilicon.23.of.41.TheFoundry` — The Foundry
- `HYSTERON.SandToSilicon.24.of.41.TheProbe` — The Probe
- `HYSTERON.SandToSilicon.25.of.41.TheProbeCard` — The Probe Card
- `HYSTERON.SandToSilicon.26.of.41.TheCut` — The Cut
- `HYSTERON.SandToSilicon.27.of.41.TheTemporaryBond` — The Temporary Bond
- `HYSTERON.SandToSilicon.28.of.41.ThePlaceAndBond` — The Place & Bond
- `HYSTERON.SandToSilicon.29.of.41.TheStack` — The Stack
- `HYSTERON.SandToSilicon.30.of.41.TheGlass` — The Glass
- `HYSTERON.SandToSilicon.31.of.41.TheFoil` — The Foil
- `HYSTERON.SandToSilicon.32.of.41.TheDielectric` — The Dielectric
- `HYSTERON.SandToSilicon.33.of.41.ThePlate` — The Plate
- `HYSTERON.SandToSilicon.34.of.41.TheSubstrate` — The Substrate
- `HYSTERON.SandToSilicon.35.of.41.TheIntegrate` — The Integrate
- `HYSTERON.SandToSilicon.36.of.41.TheMold` — The Mold
- `HYSTERON.SandToSilicon.37.of.41.TheAttach` — The Attach
- `HYSTERON.SandToSilicon.38.of.41.TheFinalTest` — The Final Test
- `HYSTERON.SandToSilicon.39.of.41.TheServer` — The Server
- `HYSTERON.SandToSilicon.40.of.41.TheLink` — The Link
- `HYSTERON.SandToSilicon.41.of.41.TheIntelligence` — The Intelligence

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cd gen
python HYSTERON.SandToSilicon.01.of.41.TheOre.py
python contact.py sheet 1 2 3 4
```

## Seeds are private

Every random choice comes from a seeded generator, but the seeds used for the
originals are **not published** (`SEED = None  # private, not published`). Running the code
gives you a new variation of each plate every time - never the exact original.
That keeps the minted originals unique.

## Previews

`previews/` holds small JPEG previews of the 41 originals, named like the generators
(`HYSTERON.SandToSilicon.NN.of.41.PieceName.jpg`).

## Collection

- Rarible: https://rarible.com/user/0xcf99117D4Ae30f5Ad0088D0b461C9b2C3ce8912C
- Wallet: 0xcf99117D4Ae30f5Ad0088D0b461C9b2C3ce8912C

## License

- **Code** (`gen/`, `requirements.txt`): MIT - see `LICENSE`.
- **Artwork** (the images in `previews/` and the original plates): CC BY-NC 4.0 -
  see `LICENSE-ART`. Share with credit to HYSTERON, non-commercial use only.
  Owning the code does not grant rights to the original artworks.
