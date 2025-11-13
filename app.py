from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import os
from datetime import datetime

# 🔒 直接写死账号密码（简单粗暴，适合个人使用）
TEACHER_USERNAME = "aqnu_teacher"
TEACHER_PASSWORD = "J7$mQ!vL9@pK2#nR"  # 这就是你的强密码，别改！

DATA_FILE = "assignments.txt"
app = Flask(__name__)
app.secret_key = "xH4#9Lm$2qP!vN8sKbY6&cRwEaZ3*FjU"  # 固定 SECRET_KEY

# ========== 工具函数 ==========
def parse_line(line):
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 3:
        return None
    name, course, date_str = parts[0], parts[1], parts[2]
    repeat = parts[3] if len(parts) > 3 else "none"
    try:
        due_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return {
            "name": name,
            "course": course,
            "due_date": due_date.isoformat(),
            "repeat_type": repeat if repeat in ("weekly", "monthly") else "none"
        }
    except:
        return None

def load_assignments():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assignments = [parse_line(line) for line in lines if line.strip()]
    return [a for a in assignments if a]

def save_assignments(assignments):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        for a in assignments:
            f.write(f"{a['name']}|{a['course']}|{a['due_date']}|{a['repeat_type']}\n")

# ========== 登录装饰器 ==========
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== 路由 ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == TEACHER_USERNAME and password == TEACHER_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash("用户名或密码错误", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    assignments = load_assignments()
    assignments.sort(key=lambda x: x['due_date'])
    return render_template('index.html', assignments=assignments, current_time=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"))

@app.route('/api/add', methods=['POST'])
@login_required
def add_assignment():
    data = request.json
    name = data.get('name', '').strip()
    course = data.get('course', '').strip()
    due_date = data.get('due_date', '')
    repeat = data.get('repeat', 'none')

    if not name or not course or not due_date:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except:
        return jsonify({"error": "日期格式错误，应为 YYYY-MM-DD"}), 400

    assignments = load_assignments()
    assignments.append({
        "name": name,
        "course": course,
        "due_date": due_date,
        "repeat_type": repeat if repeat in ("weekly", "monthly") else "none"
    })
    save_assignments(assignments)
    return jsonify({"success": True})

@app.route('/api/delete/<int:index>', methods=['DELETE'])
@login_required
def delete_assignment(index):
    assignments = load_assignments()
    if 0 <= index < len(assignments):
        assignments.pop(index)
        save_assignments(assignments)
        return jsonify({"success": True})
    return jsonify({"error": "无效索引"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)