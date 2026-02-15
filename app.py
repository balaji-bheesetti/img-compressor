from flask import Flask, render_template, request, send_file
import base64
from PIL import Image
import io

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress():
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
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template(
        "index.html",
        preview_image=img_base64,
        final_size=final_size_kb,
        filename="compressed_" + file.filename,
    )


if __name__ == "__main__":
    app.run()
