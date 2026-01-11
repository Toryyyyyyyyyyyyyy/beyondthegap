from waitress import serve
import app  # 导入你的Flask主程序（app.py）

# 配置：绑定0.0.0.0（允许外网访问），端口5000，可自定义
if __name__ == '__main__':
    serve(app.app, host='0.0.0.0', port=5000, threads=4)  # threads=4表示4个线程，可根据CPU调整