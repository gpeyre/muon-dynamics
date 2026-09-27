"""Package the compiled paper's local inputs, excluding drafts and reviews."""

from pathlib import Path
import tarfile


def main():
    root = Path(__file__).resolve().parent
    recorder = root / "paper.fls"
    if not recorder.exists() or not (root / "paper.bbl").exists():
        raise SystemExit("Build the paper first with `make` in neurips/.")
    inputs = {root / "references.bib", root / "paper.bbl"}
    for line in recorder.read_text().splitlines():
        if not line.startswith("INPUT "):
            continue
        path = Path(line.removeprefix("INPUT "))
        path = (root / path).resolve()
        if not path.is_relative_to(root) or path.name == "paper.pdf":
            continue
        if path.suffix in {".tex", ".sty", ".bbl", ".bib", ".pdf", ".png", ".jpg"}:
            inputs.add(path)
    required = {root / name for name in ("paper.tex", "notation_section.tex", "neurips_2026.sty")}
    if not required.issubset(inputs) or any(not path.is_file() for path in inputs):
        raise SystemExit("Incomplete recorder inputs; rebuild before packaging.")
    output = root / "arxiv-source.tar.gz"
    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(inputs):
            archive.add(path, arcname=str(path.relative_to(root)), recursive=False)
    print(f"Created {output} ({len(inputs)} files). Main source: paper.tex")


if __name__ == "__main__":
    main()
