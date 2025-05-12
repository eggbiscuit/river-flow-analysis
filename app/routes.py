from flask import request, jsonify, url_for, Response
from werkzeug.utils import secure_filename
import os
import uuid
from app.utils import process_video_and_store


def allowed_file(filename):
    """检查文件是否为允许的类型"""
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def register_routes(app):
    """注册 Flask 路由"""

    @app.route('/upload', methods=['POST'])
    def upload_video():
        """处理视频上传和处理"""
        try:
            print("📥 Received /upload POST request")

            if 'video' not in request.files:
                print("❌ No video file part in request")
                return jsonify({'error': 'No video file part in request'}), 400

            file = request.files['video']
            if file.filename == '':
                print("❌ No file selected")
                return jsonify({'error': 'No file selected'}), 400

            if not allowed_file(file.filename):
                print(f"❌ Unsupported file type: {file.filename}")
                return jsonify({'error': 'Unsupported file type'}), 400

            # 保存上传文件
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            upload_folder = app.config.get('UPLOAD_FOLDER', './uploads')
            os.makedirs(upload_folder, exist_ok=True)
            input_filepath = os.path.join(upload_folder, filename)
            file.save(input_filepath)
            print(f"✅ File saved to {input_filepath}")

            # 调用 C++ 程序处理视频并存储结果
            print("⚙️ Starting video processing...")
            result = process_video_and_store(input_filepath)
            print(f"✅ Video processing complete. Processed video saved to {result['video']}")

            # 构造流式加载的 URL
            output_video_url = url_for('stream_video', filename=os.path.basename(result["video"]), _external=True)

            print(f"🌐 Processed video URL: {output_video_url}")

            return jsonify({
                'message': 'Upload and processing complete',
                'output_video': output_video_url,
                'video_id': result["video_id"]
            }), 200

        except Exception as e:
            print(f"❌ Error during upload or processing: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/stream/<path:filename>', methods=['GET'])
    def stream_video(filename):
        """流式加载视频"""
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        def generate():
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):  # 每次读取 8KB
                    yield chunk

        response = Response(generate(), content_type='video/mp4')
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response
    
    @app.route('/analyze/<int:video_id>', methods=['GET'])
    def analyze_video(video_id):
        """分析视频数据并返回统计结果"""
        from app.utils import analyze_video_data
        try:
            analysis_result = analyze_video_data(video_id)
            return jsonify(analysis_result), 200
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return jsonify({"error": str(e)}), 500