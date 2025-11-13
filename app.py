import os
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for

# 使用 /tmp 目录（Render 唯一可写位置）
DATA_FILE = os.path.join(tempfile.gettempdir(), "assignments.txt")

app = Flask(__name__)
app.secret_key = "xH4#9Lm$2qP!vN8sKbY6&cRwEaZ3*FjU"  # 保留 secret_key（Flask 需要它来用 session/flash，但这里其实不用了）

# --- 工具函数 ---
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

# --- 主页面：直接显示作业列表 ---
@app.route('/')
def index():
    assignments = load_assignments()
    assignments.sort(key=lambda x: x['due_date'])
    return render_template('index.html', assignments=assignments)

# --- 添加作业（公开接口）---
@app.route('/api/add', methods=['POST'])
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
        return jsonify({"error": "日期格式错误"}), 400

    assignments = load_assignments()
    assignments.append({"name": name, "course": course, "due_date": due_date, "repeat_type": repeat})
    save_assignments(assignments)
    return jsonify({"success": True})

# --- 删除作业（公开接口）---
@app.route('/api/delete/<int:index>', methods=['DELETE'])
def delete_assignment(index):
    assignments = load_assignments()
    if 0 <= index < len(assignments):
        assignments.pop(index)
        save_assignments(assignments)
        return jsonify({"success": True})
    return jsonify({"error": "无效索引"}), 400

# --- 启动配置 ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)