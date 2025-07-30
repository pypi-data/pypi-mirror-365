"""
Synchronous helpers that turn common document types into *flattened* PDFs.

The conversion layer is intentionally narrow: it only knows how to transform a
single :class:`pdf_tools.models.files.File` at a time and always writes the
result **to disk** (returning a new :class:`pdf_tools.models.files.File`
instance that describes the freshly-minted PDF).  Anything involving bulk or
parallel work is handled by the surrounding CLI or orchestration layer.

Supported input types & back-ends
---------------------------------
* **Microsoft Word** (``.doc``/``.docx``) → LibreOffice :mod:`unoconvert` CLI.
* **Raster images** (``.jpeg``/``.png``) → :mod:`Pillow` + :mod:`img2pdf`.

Both back-ends are platform-dependent: LibreOffice must be on ``$PATH`` and
Pillow relies on system image libraries.  Each helper therefore emits a
:meth:`typer.echo` so the CLI shows *progress* but your own code can swap it
for a custom logger.

Design notes
------------
* All functions are **blocking** and may run external processes; call them in a
  ThreadPool if you need async flows.
* The helpers never *overwrite* an existing file unless the caller explicitly
  points *output_path* to an existing location.
"""

import subprocess
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path
from typing import Final

import img2pdf  # type: ignore
import typer
from PIL import Image

from pdf_tools.convert.unoserver_ctx import assert_office_ready
from pdf_tools.models.files import File

__all__: Sequence[str] = [
    "convert_word_to_pdf",
    "convert_image_to_pdf",
    "convert_file_to_pdf",
]

SUPPORTED_IMAGE_FORMATS: set[str] = {"jpeg", "png", "jpg", "tiff", "bmp"}
_UNOCONVERT_CMD: Final[str] = "unoconvert"


def _output_dir_handler(input_path: Path, output_dir: Path) -> Path:
    """
    Create an output path from given input file and output directory.

    Takes an input file path (regardless of file type) and returns the filename
    from the input file with a PDF extension and located within the given
    output directory.

    Parameters
    ----------
    input_path : :class:`Path`
        Input file path to extract filename from.
    output_dir : :class:`Path`
        Path to output directory where the resulting file will reside in.

    Returns
    -------
    :class:`Path`
        New file path located inside the given `output_dir` and with a
        `.pdf` extension.
    """
    name = input_path.stem
    return (output_dir / name).with_suffix(".pdf")


def convert_word_to_pdf(
    file: File,
    output_path: Path | None = None,
    overwrite: bool = False,
) -> File:
    """Convert a Word document (``.doc``, ``.docx``) to PDF on disk.

    Parameters
    ----------
    file : :class:`File`
        A *Word* :class:`pdf_tools.models.files.File` (:attr:`file.type` must
        be either ``"doc"`` or ``"docx"``).
    output_path : :class:`Path` | :class:`None`, optional
        Destination path for the resulting PDF.  When *None* (default) the
        helper replaces the source extension with ``.pdf`` next to the input
        file.
    overwrite : `bool`, default ``False``
        Overwrite output file if it already exists.

    Returns
    -------
    :class:`File`
        A new :class:`pdf_tools.models.files.File` that points at the
        generated PDF and carries forward the original *bookmark_name*.

    Raises
    ------
    FileExistsError
        If `overwrite` is False and the output path already exists.
    RuntimeError
        If LibreOffice exits with a non-zero status.
    FileNotFoundError
        If `output_path`'s parent directory does not exist.
    """
    assert_office_ready()
    typer.echo(f"Converting {file.path.resolve()}")
    if output_path is not None:
        if output_path.suffix == "":
            # we think this is a directory
            new_path = (output_path / file.path.stem).with_suffix(".pdf")
        elif output_path.suffix != "":
            # we think it's a filename
            new_path = output_path
    else:
        new_path = file.absolute_path.with_suffix(".pdf")

    if new_path.exists() and overwrite is False:
        raise FileExistsError(f"File {new_path} already exists. Exiting.")
    if new_path.is_dir():
        raise ValueError(f"Path {new_path} is a directory.")
    if new_path.parent.exists() is False:
        raise FileNotFoundError(
            f"Output directory {new_path.parent} does not exist. "
            f"Please create it or choose an existing directory."
        )
    try:
        subprocess.run(
            [
                _UNOCONVERT_CMD,
                str(file.absolute_path),
                new_path,
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        raise RuntimeError(
            f"LibreOffice failed to convert '{file.path}' → '{new_path}'. "
            f"Exit code {ex.returncode}. Stderr:\n{ex.stderr.decode()}."
        ) from ex

    typer.echo(f"Converted {new_path}")
    _file_data = {"path": new_path, "bookmark_name": file.bookmark_name}
    return File.model_validate(_file_data)


def convert_image_to_pdf(
    file: File, output_path: Path | None = None, overwrite: bool = False
) -> File:
    """Convert a single raster image to a *vector-wrapped* PDF.

    The routine uses :mod:`Pillow` to normalise color mode and :mod:`img2pdf`
    to wrap the image bytes without re-encoding (lossless).

    Parameters
    ----------
    file : :class:`File`
        Source image (``jpg``, ``jpeg``, ``tiff``, ``bmp``, or ``png``).
        Other types raise ``ValueError``.
    output_path : :class:`pathlib.Path` | `None`, optional
        Destination path for the resulting PDF.  Defaults to the input path
        with ``.pdf`` extension.
    overwrite : bool, default ``False``
        Overwrite output file if it already exists.

    Returns
    -------
    File
        :class:`pdf_tools.models.files.File` for the created PDF.

    Raises
    ------
    ValueError
        If :attr:`file.type` is not a supported image format.
    OSError
        If `Pillow` cannot read or decode the image.
    FileNotFoundError
        If `output_path`'s parent directory does not exist.
    FileExistsError
        If `overwrite` is False and the output path already exists.
    """
    typer.echo(f"Converting {file.path.resolve()}")

    if output_path is not None:
        if output_path.suffix == "":
            # we think this is a directory
            new_path = (output_path / file.path.stem).with_suffix(".pdf")
        elif output_path.suffix != "":
            # we think it's a filename
            new_path = output_path
    else:
        new_path = file.absolute_path.with_suffix(".pdf")

    if new_path.exists() and overwrite is False and new_path.is_file():
        raise FileExistsError(f"File {new_path} already exists. Exiting.")
    if new_path.is_dir():
        raise ValueError(f"Path {new_path} is a directory.")
    if new_path.parent.exists() is False:
        raise FileNotFoundError(
            f"Output directory {new_path.parent} does not exist. "
            f"Please create it or choose an existing directory."
        )
    try:
        with Image.open(file.absolute_path) as image:
            if image.format.lower() not in SUPPORTED_IMAGE_FORMATS:
                raise ValueError(
                    f"Unsupported image format '{image.format}'. "
                    f"Supported formats: "
                    f"{', '.join(sorted(SUPPORTED_IMAGE_FORMATS))}."
                )
            if image.mode != "RGB":
                image = image.convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            with open(new_path, "wb") as pdf:
                pdf_bytes = img2pdf.convert(buffer.getvalue())
                pdf.write(pdf_bytes)
    except (OSError, ValueError) as ex:
        raise RuntimeError(
            f"Could not convert image '{file.path}' to PDF: {ex}."
        ) from ex
    _file_data = {"path": new_path, "bookmark_name": file.bookmark_name}
    return File.model_validate(_file_data)


def convert_file_to_pdf(
    file: File,
    output_path: Path | None = None,
    overwrite: bool = False,
) -> File:
    """Dispatch `file` to the appropriate conversion helper.

    Inspects :attr:`file.type <pdf_tools.models.files.File.type>`
    and forwards the call to either :func:`convert_word_to_pdf` or
    :func:`convert_image_to_pdf`.  Unsupported types return the `file` object
    unchanged so callers can safely chain operations.

    Parameters
    ----------
    file : :class:`File`
        Any :class:`pdf_tools.models.files.File` instance.
    output_path : `pathlib.Path` | `None`, optional
        Desired output path.  Passed verbatim to the underlying helper.
    overwrite : `bool`, default ``False``
        Overwrite output file if it already exists.

    Returns
    -------
    :class:`File`
        Either the converted PDF description or the original :class:`File` if
        no conversion rule matched.

    Raises
    ------
    ValueError
        If an unsupported file type is provided.
    """
    if file.type in ["doc", "docx"]:
        return convert_word_to_pdf(file, output_path, overwrite=overwrite)

    if file.type in ["jpg", "jpeg", "png"]:
        return convert_image_to_pdf(file, output_path, overwrite=overwrite)

    else:
        raise ValueError(f"Unsupported file type: {file.type}.")
