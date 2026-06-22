# Zip decks

Place zip files here to batch-process them with `create_pdf.py --zip_decks`.

Each zip should contain a `front/` folder, and optionally `back/`,
`double_sided/`, and a `config.json` describing per-card crop/extend_corners
groups. Use `--group` to combine all decks into a single PDF.

Processed zips are deleted after a successful run.
