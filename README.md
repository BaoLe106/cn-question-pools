# CN Field Notes

A dependency-free static flash-card site generated from the supplied CS 6250 Module 1–3 question-pool PDFs.

## Preview locally

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Add another module

1. Put `Module N Question Pool.pdf` beside this project directory.
2. Extend the `MODULES` metadata in `scripts/generate_data.py` and add any extracted figure mappings.
3. Update the module range in `scripts/extract_pdfs.py`, then run the extraction and generation scripts.
4. Add `<script src="data/module-N.js"></script>` before `app.js` in `index.html`.

Each module is isolated in its own generated data file, so existing cards and application code do not need to be rewritten.
