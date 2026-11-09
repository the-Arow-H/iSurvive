# ZIM export

Kiwix reads ZIM archives. This folder is the export target. v0.1 does not
ship a `.zim` file and does not vendor Kiwix (GPL-3.0).

The content pack is the Markdown in `content/na/` plus `sources/SOURCES.md`.
A future export can point a ZIM builder at those files without copying Kiwix
source into this repository. Content license: CC BY-SA 4.0 (`LICENSE-CONTENT`).
Code license for the guide app: MIT (`app/LICENSE`).

Do not ingest GPL code from Kiwix or from Libre Survival Manual into this tree.
