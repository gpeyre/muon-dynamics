#!/usr/bin/env python3
"""Correct an archived PDF legend without executing a simulation."""

import hashlib
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ContentStream, FloatObject, TextStringObject

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "neurips" / "figures" / "fig-mlp"
SOURCE = FIGURES / "mlp_relu_angular_hist_snapshots_combined.pdf"
TARGET = FIGURES / "mlp_relu_angular_hist_snapshots_camera_ready.pdf"


class ExactFloat(FloatObject):
    def myrepr(self):
        # Preserve parsed coordinates exactly; PDF numbers cannot use exponents.
        return format(Decimal(repr(float(self))), "f")


def preserve_precision(value):
    if isinstance(value, FloatObject):
        return ExactFloat(value)
    if isinstance(value, ArrayObject):
        return ArrayObject([preserve_precision(item) for item in value])
    return value


def correct_legend(source=SOURCE, target=TARGET):
    """Replace the literal TeX escape in the legend; retain all plotted paths."""
    reader = PdfReader(source)
    writer = PdfWriter(clone_from=reader)
    replacements = 0
    for page in writer.pages:
        stream = ContentStream(page.get_contents(), writer)
        for operands, operator in stream.operations:
            operands[:] = [preserve_precision(item) for item in operands]
            if operator != b"TJ":
                continue
            text = "".join(item for item in operands[0] if isinstance(item, str))
            if text.replace("\\", "") == "p=infty":
                # Reuse embedded glyphs: the archived Type3 font is subsetted.
                operands[0] = ArrayObject([TextStringObject("p=inf")])
                replacements += 1
        page.replace_contents(stream)
    if replacements != 1:
        raise ValueError(f"Expected exactly one legacy legend, found {replacements}")
    writer.add_metadata({
        "/Title": "Archived MLP angular histograms: corrected legend",
        "/Subject": "Only the literal p=backslash-infty legend is replaced by p=inf; no simulation.",
    })
    with target.open("wb") as handle:
        writer.write(handle)
    print(f"Source SHA-256: {hashlib.sha256(source.read_bytes()).hexdigest()}")
    print(f"Corrected one legend: {target}")


if __name__ == "__main__":
    correct_legend()
