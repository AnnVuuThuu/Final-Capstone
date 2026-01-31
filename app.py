from flask import Flask, render_template, request
import csv
import io
import math

app = Flask(__name__)

def is_number(x: str) -> bool:
    try:
        v = float(x)
        return not (math.isnan(v) or math.isinf(v))
    except Exception:
        return False

def pick_columns(headers, rows):
    # X = first column
    x_idx = 0

    # Y = first numeric column after first
    y_idx = -1
    for c in range(1, len(headers)):
        seen = 0
        numeric = 0
        for r in rows[:50]:
            if c >= len(r):
                continue
            v = (r[c] or "").strip()
            if v == "":
                continue
            seen += 1
            if is_number(v):
                numeric += 1
        if seen > 0 and (numeric / seen) >= 0.7:
            y_idx = c
            break

    return x_idx, y_idx

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/upload")
@app.post("/upload")
def upload():
    f = request.files.get("csv_file")
    if not f or f.filename.strip() == "":
        return render_template("result.html", error="No file uploaded. Please choose a CSV.")

    try:
        text = f.read().decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        data = list(reader)
    except Exception:
        return render_template("result.html", error="Could not read that file. Make sure it's a valid CSV.")

    # Remove empty rows
    data = [row for row in data if any((cell or "").strip() for cell in row)]
    if len(data) < 2:
        return render_template("result.html", error="CSV looks empty (needs header + at least 1 row).")

    headers = [(h or "").strip() for h in data[0]]
    rows = data[1:]

    # Normalize row length to header length
    norm_rows = []
    for r in rows:
        r = list(r)
        if len(r) < len(headers):
            r += [""] * (len(headers) - len(r))
        norm_rows.append(r[:len(headers)])

    # Limit rows sent to client (keeps UI fast)
    max_rows = 500
    rows_for_client = norm_rows[:max_rows]

    # preview: first 20
    preview_rows = rows_for_client[:20]

    # Pick defaults (X=0, Y=first numeric after)
    x_idx, y_idx = pick_columns(headers, rows_for_client)
    if y_idx == -1:
        # still render page; user can choose Count agg etc.
        y_idx = 1 if len(headers) > 1 else 0

    return render_template(
        "result.html",
        error=None,
        headers=headers,
        preview_rows=preview_rows,
        rows_json=rows_for_client,   # <-- NEW: full data to power chart controls
        default_x=x_idx,
        default_y=y_idx
    )


if __name__ == "__main__":
    app.run(debug=True)
