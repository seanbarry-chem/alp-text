# Atomic Layer Processing: an interactive textbook

Source for **https://atomiclayerprocessing.ca**, built with [Quarto](https://quarto.org).

## Layout

```
_quarto.yml                   site/book config (chapter list lives here)
index.qmd                     landing page
chapters/                     one .qmd per chapter (01-introduction, 02-ald-fundamentals, ...)
references.bib                BibTeX; cite with [@Key]
assets/                       theme, quiz script and styles
.github/workflows/publish.yml builds and deploys on every push to main
CNAME                         custom domain
```

## Writing

- Chapters are Markdown (`.qmd`). Equations: `$$ ... $$ {#eq-name}`, referenced as `@eq-name`.
- **Simulations:** ```` ```{ojs} ```` cells (Observable JS) run in the reader's browser; no server needed. Copy an existing `sim-box` as a template.
- **Quizzes:** a `::: {.quiz}` block with a task list (`- [x]` marks the correct answer) and an optional `::: {.explanation}` block. Answers are visible in page source; these are self-checks, not assessments.
- **Obsidian:** you can open this folder as a vault, but Quarto does not understand `[[wikilinks]]` or `![[embeds]]`. Use normal Markdown links in chapter files.

## House style

- **GPC is always reported in Å**, never Å/cycle: "per cycle" is already in the name. Applies to text, axis labels, slider labels and computed outputs. Rates per something else are written out, e.g. "Å per 100 °C".

## Preview locally

1. Install Quarto: https://quarto.org/docs/get-started/
2. In this folder: `quarto preview` (live reload) or `quarto render` (writes `_site/`).

## Publish (one-time setup)

1. Create a GitHub repository (e.g. `alp-textbook`) and push this folder to `main`.
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Repo **Settings → Pages → Custom domain:** `atomiclayerprocessing.ca`, then tick *Enforce HTTPS* once the certificate is issued.
4. At your domain registrar, set DNS:
   - `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www` → `<your-github-username>.github.io`
5. Every push to `main` now rebuilds the site (~1–2 min).

Check GitHub's current Pages docs for the IP addresses before setting DNS.

## Before going public

- [ ] Verify every entry in `references.bib` (entered from memory; check DOIs/pages).
- [ ] Check that no text or figure is copied or closely paraphrased from a copyrighted source.
- [ ] Optional: ACS citation style (download `american-chemical-society.csl` from zotero.org/styles into `assets/`, add `csl: assets/american-chemical-society.csl`).
