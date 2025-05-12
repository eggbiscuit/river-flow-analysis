import subprocess
import json
import sqlite3
from datetime import datetime
import os

def process_video_and_store(video_path):
    try:
        print(f"⚙️ Processing video: {video_path}")

        # 定义输出视频路径（存储在 uploads 文件夹中）
        output_video_path = video_path.replace(".mp4", "_processed.mp4")
        print(f"📂 Output video path: {output_video_path}")

        # 调用 C++ 光流程序
        print("⚙️ Running C++ optical flow program...")
        result = subprocess.run(
            ["./build/lk_optical_flow", video_path, output_video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )

        if result.returncode != 0:
            print(f"❌ C++ program error: {result.stderr.decode()}")
            raise RuntimeError(f"C++ error: {result.stderr.decode()}")

        output = result.stdout.decode().strip()
        print("✅ C++ program completed successfully")
        flow = json.loads(output)  # 解析返回的 JSON

        regions = flow.get("regions", [])
        print(f"📊 Detected {len(regions)} regions in the video")

        # 连接数据库
        print("📂 Connecting to database...")
        conn = sqlite3.connect("db/river_network.db")
        cursor = conn.cursor()

        # 插入 video 表记录
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO video (path, uploaded_at) VALUES (?, ?)",
            (video_path, timestamp)
        )
        video_id = cursor.lastrowid
        print(f"✅ Video record inserted into database with ID: {video_id}")

        # 插入多个区域节点
        for region in regions:
            region_x = region["region_x"]
            region_y = region["region_y"]
            region_width = region["region_width"]
            region_height = region["region_height"]
            flow_speed = region["flow_speed"]
            flow_direction = region.get("flow_direction", "UNKNOWN")  # 默认值为 UNKNOWN
            max_speed = region["max_speed"]

            cursor.execute(
                """
                INSERT INTO node (
                    video_id, region_x, region_y, region_width,
                    region_height, flow_speed, flow_direction, max_speed, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video_id, region_x, region_y, region_width,
                    region_height, flow_speed, flow_direction, max_speed, timestamp
                )
            )

        conn.commit()
        conn.close()
        print("✅ All region data inserted into database")

        return {
            "video": output_video_path,
            "video_id": video_id,
            "regions": regions
        }

    except subprocess.TimeoutExpired:
        print("❌ C++ program timed out")
        raise RuntimeError("Optical flow analysis timed out")
    except Exception as e:
        print(f"❌ Error during video processing: {str(e)}")
        raise RuntimeError(f"Error during video processing: {str(e)}")
    
def analyze_video_data(video_id):
    """分析视频数据，计算平均速度、最大速度和流量分布"""
    conn = sqlite3.connect("db/river_network.db")
    cursor = conn.cursor()

    # 查询节点数据
    cursor.execute(
        "SELECT region_x, region_y, flow_speed, max_speed, flow_direction FROM node WHERE video_id = ?", (video_id,)
    )
    nodes = cursor.fetchall()

    if not nodes:
        return {"error": "No data found for the given video ID"}

    # 计算统计数据
    flow_distribution = []
    for node in nodes:
        region = f"({node[0]}, {node[1]})"
        flow_distribution.append({
            "region": region,
            "speed": node[2],
            "max_speed": node[3],
            "direction": node[4]
        })

    conn.close()

    return {
        "flow_distribution": flow_distribution
    }