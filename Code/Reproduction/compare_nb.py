"""Compare the text outputs of the notebooks with those of another git revision.

By default the reference is 0ddfa23, the authors' last commit before the Linux re-run.

Usage (python from the pinned environment in RESULTS.md, from anywhere in the repository):
    python Code/Reproduction/compare_nb.py                       # all ten notebooks
    python Code/Reproduction/compare_nb.py Code/06_RandomForestAnalysis_ML.ipynb --show 3
    python Code/Reproduction/compare_nb.py --ref HEAD~1

For each notebook it reports how many code cells have the same text output as the reference.
Memory addresses (0x...), runs of spaces and blank lines are normalised, consecutive stdout chunks
are joined, and stderr (warnings, progress bars) is ignored. Figures are counted, not compared.
The exit code is 0 only if every notebook matches.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDRESS = re.compile(r"0x[0-9a-fA-F]+")
SPACES = re.compile(r"[ \t]+")


def all_notebooks():
    paths = sorted((REPO / "Code").glob("*.ipynb")) + sorted((REPO / "Code" / "Appendix").glob("*.ipynb"))
    return [p.relative_to(REPO).as_posix() for p in paths]


def repo_path(arg):
    path = Path(arg)
    if not path.is_absolute() and (REPO / path).exists():
        return path.as_posix()
    return path.resolve().relative_to(REPO).as_posix()


def normalise(text):
    text = ADDRESS.sub("0x?", text)
    lines = (SPACES.sub(" ", line).rstrip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def text_and_figures(cell):
    parts, figures = [], 0
    for out in cell.get("outputs", []):
        kind = out.get("output_type")
        if kind == "stream":
            if out.get("name") == "stderr":
                continue
            text = "".join(out.get("text", ""))
            if parts and parts[-1][0] == "stream":
                parts[-1][1] += text  # stdout may arrive in several chunks
            else:
                parts.append(["stream", text])
        elif kind in ("execute_result", "display_data"):
            data = out.get("data", {})
            if "image/png" in data or "image/svg+xml" in data:
                figures += 1
            elif "text/plain" in data:
                parts.append(["data", "".join(data["text/plain"])])
        elif kind == "error":
            parts.append(["error", f"ERROR {out.get('ename')}: {out.get('evalue')}"])
    return normalise("\n".join(text for _, text in parts)), figures


def code_cells(notebook):
    return [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]


def compare(path, ref, show):
    reference = json.loads(subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"],
                                          capture_output=True, text=True, check=True).stdout)
    current = json.loads((REPO / path).read_text(encoding="utf-8"))
    old_cells, new_cells = code_cells(reference), code_cells(current)
    same = different = figures_old = figures_new = shown = 0
    for number, (old, new) in enumerate(zip(old_cells, new_cells), 1):
        text_old, figs_old = text_and_figures(old)
        text_new, figs_new = text_and_figures(new)
        figures_old += figs_old
        figures_new += figs_new
        if text_old == text_new:
            same += 1
            continue
        different += 1
        if shown < show:
            shown += 1
            first_line = "".join(new["source"]).strip().splitlines()[:1]
            print(f"  code cell {number}: {first_line[0][:80] if first_line else ''}")
            print("    reference:", text_old[:300].replace("\n", "\n               "))
            print("    current  :", text_new[:300].replace("\n", "\n               "))
    count_note = "" if len(old_cells) == len(new_cells) else f", code cells {len(old_cells)} vs {len(new_cells)}"
    print(f"{path}: {same}/{same + different} code cells with the same text output, "
          f"figures {figures_old} -> {figures_new}{count_note}")
    return different == 0 and len(old_cells) == len(new_cells)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="*", help="notebooks to compare (default: all ten)")
    parser.add_argument("--ref", default="0ddfa23", help="git revision to compare with (default: 0ddfa23)")
    parser.add_argument("--show", type=int, default=0, metavar="N", help="print up to N differing cells per notebook")
    args = parser.parse_args()
    paths = [repo_path(p) for p in args.notebooks] or all_notebooks()
    results = [compare(path, args.ref, args.show) for path in paths]
    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
