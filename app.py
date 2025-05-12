from flask import Flask
from flask_cors import CORS
from app.routes import register_routes
import os

app = Flask(__name__, static_url_path='/static', static_folder='./static')

# 确保 static 目录存在
os.makedirs(app.static_folder, exist_ok=True)
app.config['STATIC_FOLDER'] = './static'  # 添加 STATIC_FOLDER 配置
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# 启用 CORS
CORS(app)

# 注册路由
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)