# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import json
from datetime import datetime, timedelta

DATA_FILE = "assignments.txt"

app = Flask(__name__)

# 工具函数：解析一行数据
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

# 读取所有作业
def load_assignments():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assignments = [parse_line(line) for line in lines if line.strip()]
    return [a for a in assignments if a]

# 保存作业
def save_assignments(assignments):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        for a in assignments:
            f.write(f"{a['name']}|{a['course']}|{a['due_date']}|{a['repeat_type']}\n")

@app.route('/')
def index():
    assignments = load_assignments()
    # 按截止日期排序
    assignments.sort(key=lambda x: x['due_date'])
    return render_template('index.html', assignments=assignments, current_time=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"))

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
def delete_assignment(index):
    assignments = load_assignments()
    if 0 <= index < len(assignments):
        assignments.pop(index)
        save_assignments(assignments)
        return jsonify({"success": True})
    return jsonify({"error": "无效索引"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)