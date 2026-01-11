from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from database import init_db, get_all_contents, get_content_by_id, add_content, update_content, delete_content, \
    toggle_content_status
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大文件大小
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 初始化数据库
init_db()


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """主页 - 显示所有内容的标题和介绍图片"""
    contents = get_all_contents(active_only=True)
    return render_template('index.html', contents=contents)


@app.route('/content/<int:content_id>')
def content_detail(content_id):
    """内容详情页"""
    content = get_content_by_id(content_id)
    if content:
        return render_template('detail.html', content=content)
    else:
        return "Page Not Found", 404


@app.route('/admin')
def admin():
    """管理页面"""
    contents = get_all_contents(active_only=False)
    return render_template('admin.html', contents=contents)


@app.route('/admin/add', methods=['GET', 'POST'])
def add_content_page():
    """添加内容页面"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        intro = request.form.get('intro', '').strip()
        detail = request.form.get('detail', '').strip()

        sort_order_str = request.form.get('sort_order', '').strip()
        sort_order = int(sort_order_str) if sort_order_str.isdigit() else None

        # 处理图片上传
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        if title and intro and detail:
            add_content(title, intro, detail, image_filename, sort_order)
            return redirect(url_for('admin'))

    return render_template('edit_content.html', content=None)


@app.route('/admin/edit/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    """编辑内容"""
    content = get_content_by_id(content_id)
    if not content:
        return "Page Not Found", 404

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        intro = request.form.get('intro', '').strip()
        detail = request.form.get('detail', '').strip()

        sort_order_str = request.form.get('sort_order', '').strip()
        sort_order = int(sort_order_str) if sort_order_str.isdigit() else content.get('sort_order', 0)

        # 处理图片上传
        image_filename = content['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        if title and intro and detail:
            update_content(content_id, title, intro, detail, image_filename, sort_order)
            return redirect(url_for('admin'))

    return render_template('edit_content.html', content=content)


@app.route('/admin/delete/<int:content_id>')
def delete_content_page(content_id):
    """删除内容"""
    delete_content(content_id)
    return redirect(url_for('admin'))


@app.route('/admin/toggle/<int:content_id>')
def toggle_content(content_id):
    """启用/停用内容"""
    toggle_content_status(content_id)
    return redirect(url_for('admin'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/contents')
def api_contents():
    """API接口：获取所有内容（JSON格式）"""
    contents = get_all_contents(active_only=False)
    return jsonify(contents)


# ========== 新增：wangEditor 图片上传API开始 ==========
@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    """处理富文本编辑器中的图片上传（wangEditor格式）"""
    if 'image' not in request.files:
        # wangEditor 期望的返回格式
        return jsonify({
            "errno": 1,
            "message": "没有上传文件"
        })

    file = request.files['image']

    if file.filename == '':
        return jsonify({
            "errno": 1,
            "message": "没有选择文件"
        })

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名冲突
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # wangEditor 期望的返回格式
        # 1. 单个图片返回格式
        image_url = url_for('uploaded_file', filename=filename)

        return jsonify({
            "errno": 0,  # 注意：wangEditor 中 0 表示成功
            "data": {
                "url": image_url,
                "alt": filename,
                "href": image_url
            }
        })

    return jsonify({
        "errno": 1,
        "message": "文件类型不允许"
    })


# ========== 新增：wangEditor 图片上传API结束 ==========

# ========== 新增：获取已上传图片列表API（可选）开始 ==========
@app.route('/api/get_images', methods=['GET'])
def get_images():
    """获取已上传的图片列表（用于编辑器图片管理）"""
    import os
    image_files = []

    try:
        # 遍历上传目录，获取所有图片文件
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_url = url_for('uploaded_file', filename=filename)
                image_files.append({
                    "url": image_url,
                    "alt": filename,
                    "href": image_url
                })
    except Exception as e:
        print(f"获取图片列表失败: {e}")

    return jsonify({
        "errno": 0,
        "data": image_files
    })


# ========== 新增：获取已上传图片列表API结束 ==========


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)