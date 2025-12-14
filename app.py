from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = []

    if request.method == "POST":
        file = request.files["file"]

        if file:
            decoded = file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded)
            headers = next(reader)
            for row in reader:
                data.append(row)

            return render_template("result.html", headers=headers, data=data)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
