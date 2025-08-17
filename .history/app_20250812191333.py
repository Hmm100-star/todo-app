from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    sort_by = request.args.get("sort", "due_date")  # Default to due_date
    if request.method == "POST":
        title = request.form["title"].strip()
        due_date = request.form["due_date"]
        do_date = request.form["do_date"]
        if title:
            tasks.append({
                "title": title,
                "due_date": due_date,
                "do_date": do_date
            })
        return redirect(url_for("index", sort=sort_by))

    # Sorting logic
    tasks_sorted = sorted(
        tasks,
        key=lambda x: x[sort_by] if x[sort_by] else "9999-12-31"
    )

    return render_template("index.html", tasks=tasks_sorted, sort_by=sort_by)

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
