#include <opencv2/opencv.hpp>
#include <iostream>
#include <cmath>
#include "json.hpp"

using namespace cv;
using namespace std;
using json = nlohmann::json;

// 计算流向
string calculateDirection(float dx, float dy) {
    if (abs(dx) > abs(dy)) {
        return dx > 0 ? "EAST" : "WEST";
    } else {
        return dy > 0 ? "SOUTH" : "NORTH";
    }
}

int main(int argc, char** argv) {
    if (argc < 3) {
        cerr << "Usage: ./lk_optical_flow <input_video_path> <output_video_path>" << endl;
        return -1;
    }

    string inputVideoPath = argv[1];
    string outputVideoPath = argv[2];

    VideoCapture cap(inputVideoPath);
    if (!cap.isOpened()) {
        cerr << "Error opening video" << endl;
        return -1;
    }

    int frameWidth = static_cast<int>(cap.get(CAP_PROP_FRAME_WIDTH));
    int frameHeight = static_cast<int>(cap.get(CAP_PROP_FRAME_HEIGHT));
    int fps = static_cast<int>(cap.get(CAP_PROP_FPS));

    // 修改编码器为 H.264
    VideoWriter writer(outputVideoPath, VideoWriter::fourcc('X', '2', '6', '4'), fps, Size(frameWidth, frameHeight));
    if (!writer.isOpened()) {
        cerr << "Error opening video writer" << endl;
        return -1;
    }

    Mat prevGray, gray, frame;
    vector<Point2f> prevPts, nextPts;
    vector<uchar> status;
    vector<float> err;

    // 读取第一帧
    cap >> frame;
    if (frame.empty()) return -1;

    cvtColor(frame, prevGray, COLOR_BGR2GRAY);
    goodFeaturesToTrack(prevGray, prevPts, 100, 0.3, 7);

    // 区域划分
    int rows = 3; // 分割成 3 行
    int cols = 3; // 分割成 3 列
    int regionWidth = frame.cols / cols;
    int regionHeight = frame.rows / rows;

    // 存储每个区域的总速度、数量和方向
    vector<float> regionSpeeds(rows * cols, 0);
    vector<int> regionCounts(rows * cols, 0);
    vector<float> regionMaxSpeeds(rows * cols, 0); // 每个区域的最大速度
    vector<string> regionDirections(rows * cols, "UNKNOWN");

    json outputJson;
    outputJson["regions"] = json::array();

    while (true) {
        cap >> frame;
        if (frame.empty()) break;

        cvtColor(frame, gray, COLOR_BGR2GRAY);
        calcOpticalFlowPyrLK(prevGray, gray, prevPts, nextPts, status, err);

        // 重置区域速度和计数
        fill(regionSpeeds.begin(), regionSpeeds.end(), 0);
        fill(regionCounts.begin(), regionCounts.end(), 0);
        fill(regionMaxSpeeds.begin(), regionMaxSpeeds.end(), 0);
        fill(regionDirections.begin(), regionDirections.end(), "UNKNOWN");

        for (size_t i = 0; i < status.size(); ++i) {
            if (status[i]) {
                float dx = nextPts[i].x - prevPts[i].x;
                float dy = nextPts[i].y - prevPts[i].y;
                float speed = sqrt(dx * dx + dy * dy);

                int regionX = static_cast<int>(nextPts[i].x) / regionWidth;
                int regionY = static_cast<int>(nextPts[i].y) / regionHeight;

                if (regionX >= 0 && regionX < cols && regionY >= 0 && regionY < rows) {
                    int regionIndex = regionY * cols + regionX;
                    regionSpeeds[regionIndex] += speed;
                    regionCounts[regionIndex]++;
                    regionMaxSpeeds[regionIndex] = max(regionMaxSpeeds[regionIndex], speed);
                    regionDirections[regionIndex] = calculateDirection(dx, dy);
                }
            }
        }

        // 在每个区域绘制速度信息
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                int regionIndex = r * cols + c;
                float avgSpeed = (regionCounts[regionIndex] > 0)
                                 ? regionSpeeds[regionIndex] / regionCounts[regionIndex]
                                 : 0;

                // 绘制矩形
                rectangle(frame, Point(c * regionWidth, r * regionHeight),
                          Point((c + 1) * regionWidth, (r + 1) * regionHeight),
                          Scalar(255, 0, 0), 2);

                // 绘制速度文本
                string speedText = "Speed: " + to_string(avgSpeed);
                putText(frame, speedText, Point(c * regionWidth + 10, r * regionHeight + 50),
                        FONT_HERSHEY_SIMPLEX, 1.5, Scalar(0, 0, 0), 3);

                // 添加到 JSON 输出
                json regionJson;
                regionJson["region_x"] = c * regionWidth;
                regionJson["region_y"] = r * regionHeight;
                regionJson["region_width"] = regionWidth;
                regionJson["region_height"] = regionHeight;
                regionJson["flow_speed"] = avgSpeed;
                regionJson["flow_direction"] = regionDirections[regionIndex];
                regionJson["max_speed"] = regionMaxSpeeds[regionIndex]; // 添加最大速度
                outputJson["regions"].push_back(regionJson);
            }
        }

        // 写入处理后的视频帧
        writer.write(frame);

        prevGray = gray.clone();
        goodFeaturesToTrack(prevGray, prevPts, 100, 0.3, 7);
    }

    cap.release();
    writer.release();

    // 输出 JSON 数据
    outputJson["processed_video"] = outputVideoPath;
    cout << outputJson.dump(4) << endl;

    return 0;
}