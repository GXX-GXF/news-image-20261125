#!/usr/bin/env python3
"""make.fun news-image-20261125 entry.

Writes the pre-made front-page image (entry.png, in this repository) to
/output/entry.png. Pure file copy: no network, no randomness, no clock,
so two runs produce byte-identical output. The image is validated
against the competition limits (PNG, 1024x1024, at most 1 MiB) before
and after copying, and a short summary is printed.
"""
import hashlib
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"
MAX_BYTES = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path):
    """Return (width, height) of a PNG file, or None if not a valid PNG."""
    with open(path, "rb") as fh:
        header = fh.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        return None
    length, ctype = struct.unpack(">I4s", header[8:16])
    if ctype != b"IHDR" or length != 13:
        return None
    return struct.unpack(">II", header[16:24])


def validate_image(path, label):
    """Check a PNG file against the competition limits; empty list = OK."""
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        return ["%s: cannot read file (%s)" % (label, exc)]
    failures = []
    dims = png_dimensions(path)
    if dims is None:
        failures.append("%s: not a valid PNG" % label)
    elif dims != (1024, 1024):
        failures.append("%s: dimensions %dx%d, expected 1024x1024"
                        % (label, dims[0], dims[1]))
    if size > MAX_BYTES:
        failures.append("%s: %d bytes, over the 1 MiB limit" % (label, size))
    return failures


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    failures = validate_image(SRC, "entry.png")
    if failures:
        raise SystemExit("validation failed:\n  " + "\n  ".join(failures))
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copyfile(SRC, DST)
    os.chmod(DST, 0o644)
    failures = validate_image(DST, "output")
    if failures:
        raise SystemExit("validation failed:\n  " + "\n  ".join(failures))
    dims = png_dimensions(DST)
    print("wrote %s: %dx%d, %d bytes, sha256 %s"
          % (DST, dims[0], dims[1], os.path.getsize(DST), sha256_of(DST)))


if __name__ == "__main__":
    main()
