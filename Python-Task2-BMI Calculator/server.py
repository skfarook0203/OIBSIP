"""
OASIS INFOBYTE Python Programming Internship
Task 2: BMI Calculator (Advanced Version)
Module: server.py

Lightweight Python HTTP server running on port 3000 to power the live interactive
preview in the AI Studio environment while sharing the exact same SQLite database
(database.py) and BMI calculation logic (bmi_calculator.py).
"""

import io
import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Matplotlib headless backend
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Import core business logic and database manager
from database import DatabaseManager
from bmi_calculator import (
    calculate_bmi,
    classify_bmi,
    calculate_healthy_weight_range,
    validate_user_inputs,
    get_category_color,
)

PORT = 3000
db = DatabaseManager("bmi_calculator.db")
db.seed_demo_data()

INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

def get_html_content() -> bytes:
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "rb") as f:
            return f.read()
    return b"<h1>OASIS INFOBYTE Task 2 BMI Calculator</h1>"


def generate_matplotlib_chart_bytes(user_name: str) -> bytes:
    """Generates a Matplotlib BMI trend chart PNG in memory."""
    records = db.get_user_records(user_name)

    fig = Figure(figsize=(8, 4.5), dpi=100)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#FFFFFF")

    # WHO Benchmark bands
    ax.axhspan(10, 18.5, color="#E3F2FD", alpha=0.7, label="Underweight (< 18.5)")
    ax.axhspan(18.5, 24.9, color="#E8F5E9", alpha=0.7, label="Normal weight (18.5–24.9)")
    ax.axhspan(25.0, 29.9, color="#FFF3E0", alpha=0.7, label="Overweight (25.0–29.9)")
    ax.axhspan(30.0, 48.0, color="#FFEBEE", alpha=0.7, label="Obesity (≥ 30.0)")

    if len(records) < 2:
        if len(records) == 1:
            r = records[0]
            try:
                dt = datetime.strptime(r["date_time"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                dt = datetime.now()
            ax.plot([dt], [r["bmi"]], marker="o", color="#006A61", markersize=8, label="Initial Measurement")
            ax.text(
                0.5, 0.85,
                f"1 record for {user_name} (BMI: {r['bmi']:.2f})\nAdd at least 2 measurements to plot a continuous trajectory.",
                ha="center", va="center", color="#0B1C30", fontsize=10, transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#EFF4FF", edgecolor="#006A61")
            )
        else:
            ax.text(
                0.5, 0.5,
                f"No previous records found for '{user_name}'.\nCalculate a BMI measurement to start tracking trends.",
                ha="center", va="center", color="#76777D", fontsize=11, transform=ax.transAxes
            )
        ax.set_ylim(14, 38)
    else:
        dates = []
        bmis = []
        weights = []
        for r in records:
            try:
                d = datetime.strptime(r["date_time"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                d = datetime.now()
            dates.append(d)
            bmis.append(r["bmi"])
            weights.append(r["weight"])

        ax.plot(dates, bmis, marker="o", markersize=6, color="#006A61", linewidth=2.2, label=f"BMI ({user_name})")

        for d, b, w in zip(dates, bmis, weights):
            ax.annotate(
                f"{b:.1f}\n({w:.0f}kg)",
                xy=(d, b),
                xytext=(0, 9),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
                color="#0B1C30",
            )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
        fig.autofmt_xdate(rotation=15, ha="center")
        min_y = max(12, min(bmis) - 3)
        max_y = min(46, max(bmis) + 4)
        ax.set_ylim(min_y, max_y)

    ax.set_title(f"Longitudinal BMI Trend — {user_name} ({len(records)} measurements)", fontsize=11, fontweight="bold", color="#0B1C30")
    ax.set_xlabel("Date of Measurement", fontsize=9, fontweight="bold", color="#0B1C30")
    ax.set_ylabel("Body Mass Index (BMI)", fontsize=9, fontweight="bold", color="#0B1C30")
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    return buf.getvalue()


class AppHandler(BaseHTTPRequestHandler):
    """Handles HTTP routes for live application preview and APIs."""

    def log_message(self, format, *args):
        # Clean logging
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(get_html_content())

        elif path == "/api/data":
            user_filter = query.get("user", ["All Users"])[0]
            users = db.get_all_users()
            if user_filter == "All Users" or not user_filter:
                records = db.get_all_records()
            else:
                records = list(reversed(db.get_user_records(user_filter)))

            resp = {"users": users, "records": records}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/chart.png":
            target_user = query.get("user", [""])[0].strip()
            if not target_user or target_user == "All Users":
                users = db.get_all_users()
                target_user = users[0] if users else "John"

            img_bytes = generate_matplotlib_chart_bytes(target_user)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(img_bytes)

        elif path == "/api/export_csv":
            target_user = query.get("user", ["All Users"])[0].strip()
            if target_user == "All Users" or not target_user:
                records = db.get_all_records()
                filename = "bmi_records_all.csv"
            else:
                records = db.get_user_records(target_user)
                filename = f"bmi_records_{target_user.lower()}.csv"

            csv_lines = ["ID,User Name,Weight (kg),Height (m),BMI,Category,Date Time\n"]
            for r in records:
                csv_lines.append(f'{r["id"]},"{r["user_name"]}",{r["weight"]:.1f},{r["height"]:.2f},{r["bmi"]:.2f},"{r["category"]}","{r["date_time"]}"\n')

            csv_data = "".join(csv_lines).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(csv_data)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8"))
        except Exception:
            body = {}

        if path == "/api/calculate":
            name = body.get("name", "")
            weight_str = str(body.get("weight", ""))
            height_str = str(body.get("height", ""))

            is_valid, data, error_msg = validate_user_inputs(name, weight_str, height_str)
            if not is_valid:
                resp = {"success": False, "error": error_msg}
            else:
                clean_name, weight, height = data
                bmi = calculate_bmi(weight, height)
                category = classify_bmi(bmi)
                min_w, max_w = calculate_healthy_weight_range(height)
                color = get_category_color(category)

                try:
                    record_id = db.insert_record(clean_name, weight, height, bmi, category)
                    resp = {
                        "success": True,
                        "record_id": record_id,
                        "name": clean_name,
                        "weight": weight,
                        "height": height,
                        "bmi": bmi,
                        "category": category,
                        "color": color,
                        "min_weight": min_w,
                        "max_weight": max_w,
                    }
                except Exception as e:
                    resp = {"success": False, "error": f"Database error: {e}"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/delete":
            rec_id = int(body.get("id", 0))
            success = db.delete_record(rec_id)
            resp = {"success": success, "error": None if success else "Could not delete record."}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/clear_user":
            user_name = body.get("user", "")
            success = db.clear_user_history(user_name)
            resp = {"success": success, "error": None if success else "Could not clear user history."}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


def run():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, AppHandler)
    print(f"[Server] OASIS INFOBYTE Task 2 BMI Calculator server running on http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()
