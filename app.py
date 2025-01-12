from flask import Flask, jsonify, render_template, request
import sqlite3
import socket

app = Flask(__name__)

# Hàm kết nối đến cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('scores.db')  # Tạo file scores.db nếu chưa có
    conn.row_factory = sqlite3.Row  # Để dễ dàng truy cập dữ liệu theo tên cột
    return conn

# Hàm tạo bảng scores (chỉ cần chạy một lần)
def create_scores_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fighter1 INTEGER,
                        fighter2 INTEGER
                    )''')
    conn.commit()
    conn.close()

# API để lấy điểm số hiện tại của các fighter
@app.route("/api/state", methods=["GET"])
def get_scores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scores ORDER BY id DESC LIMIT 1")  # Lấy bản ghi mới nhất
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({"fighter1": row["fighter1"], "fighter2": row["fighter2"]})
    return jsonify({"fighter1": 0, "fighter2": 0})  # Nếu không có dữ liệu, trả về điểm mặc định

# API để cập nhật điểm số cho các fighter
@app.route("/api/state", methods=["POST"])
def update_scores():
    try:
        new_scores = request.get_json()
        print(new_scores)
        
        # Lấy điểm mới
        fighter1_score = new_scores.get("fighter1", 0)
        fighter2_score = new_scores.get("fighter2", 0)

        # Lưu điểm mới vào cơ sở dữ liệu
        conn = get_db_connection()
        conn.execute('INSERT INTO scores (fighter1, fighter2) VALUES (?, ?)', 
                     (fighter1_score, fighter2_score))
        conn.commit()
        conn.close()

        return jsonify({"message": "Scores updated successfully", "newScores": new_scores})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API để thêm điểm cho một fighter
@app.route("/api/add_points", methods=["POST"])
def add_points():
    try:
        data = request.get_json()
        fighter = data["fighter"]
        points = data["points"]

        if fighter not in ["fighter1", "fighter2"]:
            return jsonify({"error": "Fighter not found"}), 400

        # Lấy điểm hiện tại
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scores ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            if fighter == "fighter1":
                new_fighter1_score = row["fighter1"] + points
                conn.execute('INSERT INTO scores (fighter1, fighter2) VALUES (?, ?)', 
                             (new_fighter1_score, row["fighter2"]))
            elif fighter == "fighter2":
                new_fighter2_score = row["fighter2"] + points
                conn.execute('INSERT INTO scores (fighter1, fighter2) VALUES (?, ?)', 
                             (row["fighter1"], new_fighter2_score))
            conn.commit()
        else:
            # Nếu chưa có bản ghi, khởi tạo điểm ban đầu
            if fighter == "fighter1":
                conn.execute('INSERT INTO scores (fighter1, fighter2) VALUES (?, ?)', 
                             (points, 0))
            elif fighter == "fighter2":
                conn.execute('INSERT INTO scores (fighter1, fighter2) VALUES (?, ?)', 
                             (0, points))
        
        conn.close()

        return jsonify({"message": "Points added successfully", "newScores": {"fighter1": new_fighter1_score, "fighter2": new_fighter2_score}})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/")
def home():
    return render_template("index.html")  # Định tuyến đến trang index.html

if __name__ == "__main__":
    create_scores_table()  # Tạo bảng khi chạy lần đầu
    # Chạy Flask trên địa chỉ IP nội bộ của máy tính
    ip = socket.gethostbyname(socket.gethostname())
    app.run(host=ip, port=5000)
