"""Post-render step: list each chapter's level-2 sections in _site/sections.json.

assets/sidebar-sections.html reads this file to add a collapsible section list
under every chapter in the left sidebar. Uses the standard library only.
"""
import html
import json
import os
import re
from pathlib import Path

out = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
H2 = re.compile(r'<h2[^>]*data-anchor-id="([^"]+)"[^>]*>(.*?)</h2>', re.S)
NUM = re.compile(r'<span class="header-section-number">(.*?)</span>', re.S)
TAG = re.compile(r"<[^>]+>")

sections = {}
for page in sorted(out.rglob("*.html")):
    rel = page.relative_to(out).as_posix()
    if not rel.startswith("chapters/"):
        continue
    items = []
    for anchor, inner in H2.findall(page.read_text(encoding="utf-8")):
        m = NUM.search(inner)
        num = html.unescape(TAG.sub("", m.group(1))).strip() if m else ""
        title = html.unescape(TAG.sub("", NUM.sub("", inner))).strip()
        items.append({"id": anchor, "num": num, "title": title})
    sections[rel] = items

# Partial renders only rebuild some pages: keep entries for the others.
manifest = out / "sections.json"
if manifest.exists():
    old = json.loads(manifest.read_text(encoding="utf-8"))
    old.update(sections)
    sections = {k: v for k, v in old.items() if (out / k).exists()}
manifest.write_text(json.dumps(sections, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"sidebar_sections: {sum(len(v) for v in sections.values())} sections in {len(sections)} chapters")
