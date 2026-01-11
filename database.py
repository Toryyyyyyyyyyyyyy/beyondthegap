import sqlite3
import os

DATABASE = 'content.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使查询结果以字典形式返回
    return conn


def init_db():
    """初始化数据库，创建表"""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建内容表
        cursor.execute('''
        CREATE TABLE contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            intro TEXT NOT NULL,
            detail TEXT NOT NULL,
            image TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 插入一些示例数据
        sample_contents = [
            ("欢迎来到内容网站", "这是一个展示各种有趣内容的地方",
             "这是一个完整的Flask内容发布网站，适合孩子学习Python和Web开发。你可以在这里发布和展示各种有趣的内容。",
             "sample1.jpg",1, 1),
            ("如何学习Python", "Python是适合初学者的编程语言",
             "Python是一种简单易学的编程语言，适合所有年龄段的人学习。你可以从基础语法开始，逐步学习更高级的概念。",
             "sample2.jpg",5, 1),
            ("有趣的科学实验", "在家就能做的简单科学实验",
             "这里介绍几个可以在家完成的简单科学实验，如火山喷发实验、彩虹牛奶实验等，既安全又有趣。",
             "sample3.jpg",10, 1),
        ]

        for content in sample_contents:
            cursor.execute('''
            INSERT INTO contents (title, intro, detail, image, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', content)

        conn.commit()
        conn.close()
        print("数据库初始化完成，已创建示例数据")


def get_all_contents(active_only=True):
    """获取所有内容"""
    conn = get_db_connection()

    if active_only:
        cursor = conn.execute('SELECT * FROM contents WHERE is_active = 1 ORDER BY sort_order ASC')
    else:
        cursor = conn.execute('SELECT * FROM contents ORDER BY sort_order ASC')

    contents = cursor.fetchall()
    conn.close()

    # 转换为字典列表
    result = []
    for content in contents:
        result.append(dict(content))

    return result


def get_content_by_id(content_id):
    """根据ID获取内容"""
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM contents WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    conn.close()

    if content:
        return dict(content)
    return None


def add_content(title, intro, detail, image=None, sort_order=None):
    """添加新内容"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 找出数据库中内容排序字段的最大值，然后加5
    if sort_order is None:
        cursor.execute('SELECT MAX(sort_order) FROM contents')
        max_order = cursor.fetchone()[0] or 0
        sort_order = max_order + 5

    cursor.execute('''
    INSERT INTO contents (title, intro, detail, image, sort_order)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, intro, detail, image, sort_order))

    conn.commit()
    content_id = cursor.lastrowid
    conn.close()

    return content_id


def update_content(content_id, title, intro, detail, image=None, sort_order=None):
    """更新内容"""
    conn = get_db_connection()

    cursor = conn.cursor()

    # 先获取现有数据，如果sort_order没有提供则保持原值
    if sort_order is None:
        cursor.execute('SELECT sort_order FROM contents WHERE id = ?', (content_id,))
        current = cursor.fetchone()
        sort_order = current[0] if current else 0

    if image:
        conn.execute('''
        UPDATE contents 
        SET title = ?, intro = ?, detail = ?, image = ?, sort_order = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (title, intro, detail, image, sort_order, content_id))
    else:
        conn.execute('''
        UPDATE contents 
        SET title = ?, intro = ?, detail = ?, sort_order = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (title, intro, detail, sort_order, content_id))

    conn.commit()
    conn.close()


def delete_content(content_id):
    """删除内容"""
    conn = get_db_connection()
    conn.execute('DELETE FROM contents WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()


def toggle_content_status(content_id):
    """切换内容的启用/停用状态"""
    conn = get_db_connection()

    # 先获取当前状态
    cursor = conn.execute('SELECT is_active FROM contents WHERE id = ?', (content_id,))
    result = cursor.fetchone()

    if result:
        new_status = 0 if result[0] else 1
        conn.execute('UPDATE contents SET is_active = ? WHERE id = ?', (new_status, content_id))
        conn.commit()

    conn.close()


def update_sort_order(content_id, sort_order):
    """更新内容的排序顺序"""
    conn = get_db_connection()
    conn.execute('''
    UPDATE contents
    SET sort_order = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (sort_order, content_id))
    conn.commit()
    conn.close()
    return True