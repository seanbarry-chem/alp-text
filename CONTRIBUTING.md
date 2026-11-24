# Contributing

Thanks for helping build *Atomic Layer Processing*. Seán Barry is the editor; all changes are reviewed before they go live at https://atomiclayerprocessing.ca.

## How to propose a change

1. **Small fixes** (typos, a wrong number, a broken link): click the GitHub edit (pencil) icon on the file and submit a pull request.
2. **Larger work** (a new section, chapter or simulation): open an Issue first describing what you plan, so effort isn't duplicated.
3. Work on a branch, then open a pull request against `main`. Every push to `main` republishes the site, so `main` should always build.
4. Before submitting, run `quarto render` locally and check that the page builds without errors and your simulations work.

## House style

- **GPC is always reported in Å, never Å/cycle.** This applies to text, axis labels, slider labels and computed outputs. Write out other rates in full, e.g. "Å per 100 °C".
- Audience: graduate students and researchers. Assume surface chemistry background; define ALD-specific terms on first use.
- Cite primary literature where possible with `[@Key]`; add the entry to `references.bib` with its DOI.
- Every simulation needs an **Assumptions** note that says what the model leaves out.
- Colours: Carleton palette only (red `#E91C24`, black, white, neutral greys). No logos or university graphics.

## Content rules

- **Original work only.** Do not copy text, figures or data plots from papers, books or slides, even with a citation. Redraw figures and write text in your own words. If you need to reuse a published figure, get written permission and note it in the caption.
- Licence: by contributing you agree your contribution is released under the site licence (CC BY-NC-SA 4.0).

## Credit

- **Invited authors receive equal credit.** All invited authors, including the editor, are listed as co-authors of the book in alphabetical order by surname. The order does not reflect the size of anyone's contribution.
- **Other contributors** (people who submit fixes or suggestions without an invitation) are thanked by name in the Acknowledgements on the Welcome page. Add yourself in your pull request.
- Becoming an invited author is at the editor's discretion.

## File layout

- `chapters/NN-short-name.qmd`: one file per chapter; add new chapters to the list in `_quarto.yml`.
- `assets/`: theme, quiz script and styles.
- Quizzes: see the `::: {.quiz}` blocks in Chapter 2 (`chapters/02-ald-fundamentals.qmd`) for the format.

## Sidebar section lists

The collapsible section lists under each chapter in the left sidebar are generated automatically at render time by `scripts/sidebar_sections.py` (needs Python 3, standard library only). Every level-2 heading (`##`) in a file under `chapters/` appears in the list; there is nothing to update by hand.
