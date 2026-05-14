from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf2image import convert_from_bytes
from PIL import Image
import io
import zipfile
import subprocess
import tempfile

app = Flask(__name__)

# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# TOOL PAGES (UI PAGES)
# -----------------------------

@app.route("/merge-page")
def merge_page():
    return render_template("merge.html")


@app.route("/split-page")
def split_page():
    return render_template("split.html")


@app.route("/compress-page")
def compress_page():
    return render_template("compress.html")


@app.route("/rotate-page")
def rotate_page():
    return render_template("rotate.html")


@app.route("/lock-page")
def lock_page():
    return render_template("lock.html")


@app.route("/unlock-page")
def unlock_page():
    return render_template("unlock.html")


@app.route("/pdf-to-image-page")
def pdf_to_image_page():
    return render_template("pdf_to_image.html")


@app.route("/image-to-pdf-page")
def image_to_pdf_page():
    return render_template("image_to_pdf.html")


# -----------------------------
# PROCESSING ROUTES
# -----------------------------

# MERGE PDF
@app.route("/merge", methods=["POST"])
def merge_pdfs():

    files = request.files.getlist("files")

    merger = PdfMerger()

    for file in files:
        merger.append(file)

    output = io.BytesIO()
    merger.write(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="merged.pdf",
        mimetype="application/pdf"
    )


# SPLIT PDF
@app.route("/split", methods=["POST"])
def split_pdf():

    file = request.files.get("file")

    reader = PdfReader(file)

    memory_zip = io.BytesIO()

    with zipfile.ZipFile(memory_zip, "w") as zf:

        for i, page in enumerate(reader.pages):

            writer = PdfWriter()
            writer.add_page(page)

            page_bytes = io.BytesIO()
            writer.write(page_bytes)

            zf.writestr(f"page_{i+1}.pdf", page_bytes.getvalue())

    memory_zip.seek(0)

    return send_file(
        memory_zip,
        as_attachment=True,
        download_name="split_pages.zip",
        mimetype="application/zip"
    )


# LOCK PDF
@app.route("/lock", methods=["POST"])
def lock_pdf():

    file = request.files.get("file")
    password = request.form.get("password")

    reader = PdfReader(file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="locked.pdf",
        mimetype="application/pdf"
    )


# UNLOCK PDF
@app.route("/unlock", methods=["POST"])
def unlock_pdf():

    file = request.files.get("file")
    password = request.form.get("password")

    reader = PdfReader(file)

    if reader.is_encrypted:
        reader.decrypt(password)

    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="unlocked.pdf",
        mimetype="application/pdf"
    )


# ROTATE PDF
@app.route("/rotate", methods=["POST"])
def rotate_pdf():

    file = request.files.get("file")
    angle = int(request.form.get("angle", 90))

    reader = PdfReader(file)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="rotated.pdf",
        mimetype="application/pdf"
    )


# PDF TO IMAGE
@app.route("/pdf-to-image", methods=["POST"])
def pdf_to_image():

    file = request.files.get("file")

    images = convert_from_bytes(file.read())

    memory_zip = io.BytesIO()

    with zipfile.ZipFile(memory_zip, "w") as zf:

        for i, img in enumerate(images):

            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")

            zf.writestr(f"page_{i+1}.png", img_bytes.getvalue())

    memory_zip.seek(0)

    return send_file(
        memory_zip,
        as_attachment=True,
        download_name="images.zip",
        mimetype="application/zip"
    )


# IMAGE TO PDF
@app.route("/image-to-pdf", methods=["POST"])
def image_to_pdf():

    files = request.files.getlist("images")

    images = []

    for file in files:
        img = Image.open(file).convert("RGB")
        images.append(img)

    output = io.BytesIO()

    images[0].save(
        output,
        save_all=True,
        append_images=images[1:],
        format="PDF"
    )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="converted.pdf",
        mimetype="application/pdf"
    )


# COMPRESS PDF
@app.route("/compress", methods=["POST"])
def compress_pdf():

    file = request.files.get("file")
    level = request.form.get("compression", "2")

    quality_map = {
        "1": "/prepress",
        "2": "/printer",
        "3": "/ebook",
        "4": "/screen"
    }

    setting = quality_map.get(level, "/ebook")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as input_file:
        file.save(input_file.name)

    output_path = input_file.name.replace(".pdf", "_compressed.pdf")

    subprocess.call([
        "gswin64c",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_file.name
    ])

    return send_file(
        output_path,
        as_attachment=True,
        download_name="compressed.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)