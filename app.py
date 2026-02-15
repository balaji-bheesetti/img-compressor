from flask import Flask, render_template, request, send_file
from PIL import Image
import io

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

compressed_buffer = None
compressed_name = None
final_kb = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress():
    global compressed_buffer, compressed_name, final_kb
    file = request.files["image"]

    try:
        img = Image.open(file).convert("RGB")
    except Exception:
        return "Invalid image file"
    target_kb = request.form.get("target_kb")
    width = request.form.get("width")
    height = request.form.get("height")

    if width and height:
        width = int(width)
        height = int(height)
        img = img.resize((width, height))
    elif width:
        width = int(width)
        ratio = width / img.width
        height = int(img.height * ratio)
        img = img.resize((width, height))
    elif height:
        height = int(height)
        ratio = height / img.height
        width = int(img.width * ratio)
        img = img.resize((width, height))

    buffer = io.BytesIO()

    if target_kb:
        target_kb = int(target_kb)
        q = 90
        while q > 5:
            buffer.seek(0)
            buffer.truncate()
            img.save(buffer, format="JPEG", quality=q, optimize=True)
            size_kb = buffer.tell() / 1024
            if size_kb <= target_kb:
                break
            q -= 3
        if q <= 5:
            buffer.seek(0)
            buffer.truncate()
            img.save(buffer, format="JPEG", quality=5, optimize=True)
    else:
        img.save(buffer, format="JPEG", quality=70, optimize=True)
    final_size_kb = round(buffer.tell() / 1024, 2)
    buffer.seek(0)
    compressed_buffer = buffer
    compressed_name = "compressed_" + file.filename

    return render_template("index.html", show_download=True, final_size=final_size_kb)


@app.route("/download")
def download():
    global compressed_buffer, compressed_name
    if not compressed_buffer:
        return "no file"
    compressed_buffer.seek(0)
    return send_file(
        compressed_buffer,
        as_attachment=True,
        download_name=compressed_name,
        mimetype="image/jpeg",
    )


if __name__ == "__main__":
    app.run()
