from flask import Flask, send_file, jsonify, render_template, request
import sqlite3
import socket
import qrcode
from io import BytesIO

app = Flask(__name__)

# Hàm kết nối đến cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('scores.db')  # Tạo file scores.db nếu chưa có
    conn.row_factory = sqlite3.Row  # Để dễ dàng truy cập dữ liệu theo tên cột
    return conn

# Hàm tạo bảng FighterCurrent, History và MatchTimer
def create_tables():
    conn = get_db_connection()

    # Tạo bảng FighterCurrent (bảng trận đấu hiện tại)
    conn.execute('''CREATE TABLE IF NOT EXISTS FighterCurrent (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fighter1_name TEXT,
                        fighter1_team TEXT,
                        fighter2_name TEXT,
                        fighter2_team TEXT,
                        weight_class TEXT,
                        round TEXT,
                        fighter1_score INTEGER,
                        fighter2_score INTEGER
                    )''')

    # Tạo bảng History (bảng lịch sử các trận đấu đã kết thúc)
    conn.execute('''CREATE TABLE IF NOT EXISTS History (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fighter1_name TEXT,
                        fighter1_team TEXT,
                        fighter2_name TEXT,
                        fighter2_team TEXT,
                        weight_class TEXT,
                        round TEXT,
                        fighter1_score INTEGER,
                        fighter2_score INTEGER
                    )''')

    # Tạo bảng MatchTimer (bảng lưu trữ thời gian của các hiệp đấu)
    conn.execute('''CREATE TABLE IF NOT EXISTS MatchTimer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        round TEXT,
                        start_time TEXT,
                        end_time TEXT
                    )''')

    conn.commit()
    conn.close()

# API để cập nhật thông tin trận đấu hiện tại
@app.route("/api/update_current_fighter", methods=["POST"])
def add_current_fighter():
    try:
        # Lấy dữ liệu từ body request
        data = request.get_json()

        fighter1_name = data["fighter1_name"]
        fighter1_team = data["fighter1_team"]
        fighter2_name = data["fighter2_name"]
        fighter2_team = data["fighter2_team"]
        weight_class = data["weight_class"]
        round = data["round"]
        fighter1_score = data.get("fighter1_score", 0)  # Mặc định là 0 nếu không có
        fighter2_score = data.get("fighter2_score", 0)  # Mặc định là 0 nếu không có

        # Kết nối tới cơ sở dữ liệu
        conn = get_db_connection()

        # Xóa tất cả các bản ghi cũ trong bảng FighterCurrent (chỉ giữ 1 bản ghi)
        conn.execute('DELETE FROM FighterCurrent')

        # Lưu thông tin mới vào bảng FighterCurrent
        conn.execute('''INSERT INTO FighterCurrent 
                        (fighter1_name, fighter1_team, fighter2_name, fighter2_team, weight_class, round, fighter1_score, fighter2_score) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (fighter1_name, fighter1_team, fighter2_name, fighter2_team, weight_class, round, fighter1_score, fighter2_score))
        conn.commit()
        conn.close()

        return jsonify({"message": "Current match added successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API để lấy điểm số hiện tại của các fighter
@app.route("/api/score", methods=["GET"])
def get_scores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM FighterCurrent ORDER BY id DESC LIMIT 1")  # Lấy bản ghi mới nhất
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "fighter1_name": row["fighter1_name"],
            "fighter1_team": row["fighter1_team"],
            "fighter2_name": row["fighter2_name"],
            "fighter2_team": row["fighter2_team"],
            "weight_class": row["weight_class"],
            "round": row["round"],
            "fighter1_score": row["fighter1_score"],
            "fighter2_score": row["fighter2_score"]
        })
    return jsonify({
        "fighter1_name": "",
        "fighter2_name": "",
        "fighter1_score": 0,
        "fighter2_score": 0
    })  # Nếu không có dữ liệu, trả về điểm mặc định

# API để cập nhật điểm số cho các fighter
@app.route("/api/score", methods=["POST"])
def update_scores():
    try:
        new_scores = request.get_json()
        # Lấy dữ liệu từ body request
        fighter1_score = new_scores.get("fighter1_score", 0)
        fighter2_score = new_scores.get("fighter2_score", 0)

        # Lấy điểm hiện tại từ bảng FighterCurrent
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FighterCurrent ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            # Chỉ cập nhật điểm số mà không thay đổi tên đấu sĩ
            updated_fighter1_score = int(row["fighter1_score"]) + fighter1_score
            updated_fighter2_score = int(row["fighter2_score"]) + fighter2_score

            # Cập nhật bảng FighterCurrent với điểm mới
            cursor.execute('UPDATE FighterCurrent SET fighter1_score = ?, fighter2_score = ? WHERE id = ?',
                           (updated_fighter1_score, updated_fighter2_score, row["id"]))
            conn.commit()
        else:
            # Nếu chưa có bản ghi, trả về lỗi
            return jsonify({"error": "No match found to update scores."}), 400

        conn.close()

        return jsonify({"message": "Scores updated successfully", 
                        "newScores": {"fighter1_score": updated_fighter1_score, "fighter2_score": updated_fighter2_score}})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API để kết thúc trận đấu và lưu điểm vào bảng History
@app.route("/api/finish", methods=["POST"])
def finish_match():
    try:
        # Lấy dữ liệu từ body request
        data = request.get_json()

        # Lấy thông tin trận đấu và điểm số
        fighter1_name = data["fighter1_name"]
        fighter1_team = data["fighter1_team"]
        fighter2_name = data["fighter2_name"]
        fighter2_team = data["fighter2_team"]
        weight_class = data["weight_class"]
        round = data["round"]
        fighter1_score = data["fighter1_score"]
        fighter2_score = data["fighter2_score"]

        # Lưu thông tin vào bảng History
        conn = get_db_connection()
        conn.execute('''INSERT INTO History 
                        (fighter1_name, fighter1_team, fighter2_name, fighter2_team, weight_class, round, fighter1_score, fighter2_score) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (fighter1_name, fighter1_team, fighter2_name, fighter2_team, weight_class, round, fighter1_score, fighter2_score))
        conn.commit()

        # Reset bảng FighterCurrent
        conn.execute('DELETE FROM FighterCurrent')
        conn.commit()

        conn.close()

        return jsonify({"message": "Match finished and scores saved to history."})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API để lưu trữ thời gian của các hiệp đấu
@app.route("/api/timer", methods=["GET"])
def get_timer():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MatchTimer")
        rows = cursor.fetchone()
        conn.close()

        return jsonify({"round": rows["round"], "start_time": rows["start_time"], "end_time": rows["end_time"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API để bắt đầu trận đấu và lưu thời gian
@app.route("/api/start_fight", methods=["POST"])
def start_fight():
    try:
        data = request.get_json()
        round = data.get("round", "round_1")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")


        # Reset bảng FighterCurrent
        
        conn = get_db_connection()
        conn.execute('DELETE FROM MatchTimer')
        conn.commit()
        conn.execute('''INSERT INTO MatchTimer (round, start_time, end_time)
                        VALUES (?, ?, ?)''', (round, start_time, end_time))
        conn.commit()
        conn.close()

        return jsonify({
            "message": f"Fight started for {round}",
            "start_time": start_time,
            "end_time": end_time
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Trang chủ
@app.route("/")
def home():
    return render_template("index.html")

# Trang admin
@app.route("/admin")
def admin():
    return render_template("admin.html")

def generate_qr_code():
    ip = socket.gethostbyname(socket.gethostname())
    url = f'http://{ip}:5000'

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

@app.route("/qr")
def qr_code():
    buffer = generate_qr_code()
    return send_file(buffer, mimetype="image/png")

if __name__ == "__main__":
    create_tables()  # Tạo bảng khi chạy lần đầu
    ip = socket.gethostbyname(socket.gethostname())
    app.run(host=ip, port=5000)
