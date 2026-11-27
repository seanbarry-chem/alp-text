#!/usr/bin/env python3
"""Export chapters to Word (.docx) for copy-editing with Track Changes.

Code blocks (simulations, inline SVG figures) are replaced by grey placeholders so
the editor sees only prose, equations, tables and quizzes. Citation keys ([@Key])
and cross-references (@sec-..., @eq-...) are kept as plain text so edits can be
mapped back to the .qmd source.

Usage: python3 tools/export_for_editing.py OUTDIR [chapter.qmd ...]
Requires pandoc (e.g. `quarto pandoc`).
"""
import re, subprocess, sys, pathlib, shutil

def strip(text):
    out, lines, i, n_sim, n_fig = [], text.split("\n"), 0, 0, 0
    while i < len(lines):
        L = lines[i]
        m = re.match(r"^(`{3,})\{(ojs|=html)\}", L)
        if m:
            fence, kind = m.group(1), m.group(2)
            i += 1
            while i < len(lines) and not lines[i].startswith(fence):
                i += 1
            i += 1
            if kind == "ojs":
                n_sim += 1
                if out and out[-1].startswith("*[Simulation code"):
                    continue
                out.append("*[Simulation code — not shown; do not edit]*")
            else:
                n_fig += 1
                out.append("*[Figure or embedded code — not shown; do not edit]*")
            continue
        out.append(L)
        i += 1
    return "\n".join(out)

def main():
    outdir = pathlib.Path(sys.argv[1]); outdir.mkdir(parents=True, exist_ok=True)
    files = sys.argv[2:] or sorted(str(p) for p in pathlib.Path("chapters").glob("*.qmd")) + ["index.qmd"]
    pandoc = shutil.which("pandoc") and ["pandoc"] or ["quarto", "pandoc"]
    for f in files:
        src = pathlib.Path(f)
        body = strip(src.read_text())
        note = ("::: {custom-style=\"Editing note\"}\n"
                f"Copy-editing copy of {src.name}. Turn on Track Changes. Edit prose freely; "
                "leave citation keys like [@Barry2022], cross-references like @sec-ald-window, "
                "and the grey placeholders as they are. Comments are welcome.\n:::\n\n")
        # put the note after any YAML front matter
        if body.startswith("---"):
            end = body.index("\n---", 3) + 4
            body = body[:end] + "\n\n" + note + body[end:]
        else:
            body = note + body
        tmp = outdir / (src.stem + ".md")
        tmp.write_text(body)
        out = outdir / (src.stem + ".docx")
        subprocess.run(pandoc + [str(tmp), "-f", "markdown-citations", "-o", str(out)], check=True)
        tmp.unlink()
        print(out)

if __name__ == "__main__":
    main()
