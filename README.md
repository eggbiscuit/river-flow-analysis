# River Flow Analysis

一个基于光流法的水流流速可视化检测系统。

## 演示图
![演示截图](docs/image.png)


## 功能
- **视频上传**：
  - 支持用户上传本地视频文件，支持多种的格式（MP4、AVI、MOV、MKV）。
  - 上传后的视频会存储在服务器的 `uploads/` 目录中，并记录到数据库中。
  - 提供上传进度显示，确保用户了解上传状态。

- **水流分析**：
  - 使用光流法（Lucas-Kanade Optical Flow）对视频中的水流进行分析。
  - 计算水流的速度和方向，并以区域为单位进行分组。
  - 支持实时分析和批量处理，适用于不同规模的视频数据。

- **数据可视化**：
  - 在前端界面中以图形化方式展示水流分析结果。
  - 提供水流速度的热力图和方向箭头，帮助用户直观了解水流的动态特性。
  - 支持按时间轴查看水流变化，便于用户分析特定时间段的水流情况。

- **区域分组**：
  - 将视频划分为多个区域节点，每个节点记录水流的速度、方向、最大速度等信息。
  - 支持按区域筛选和查看数据，便于用户聚焦特定区域的水流特性。

- **结果导出**：
  - 支持将分析结果导出为 JSON 格式，便于进一步的数据处理和分析。
  - 提供下载功能，用户可以保存分析结果到本地。

## 技术栈
- **前端**: HTML, CSS, JavaScript
- **后端**: Flask
- **视频处理**: OpenCV, C++
- **数据库**: SQLite
- **环境管理**: Conda

## 文件结构
```
river_flow_analysis/
├── app/                # 后端代码
│   ├── __init__.py     # Flask 应用初始化
│   ├── routes.py       # 路由定义
│   ├── utils.py        # 工具函数
├── sql/                # 数据库初始化脚本
│   └── init_schema.sql # 数据库表定义
├── static/             # 静态文件
├── uploads/            # 上传的视频文件
├── lk_optical_flow.cpp # 光流法实现
├── environment.yml     # Conda 环境配置
├── README.md           # 项目说明
└── .gitignore          # 忽略规则
```

## 使用方法

### 1. 克隆仓库
```bash
git clone https://github.com/eggbiscuit/river-flow-analysis.git
cd river-flow-analysis
```

### 2. 创建并激活 Conda 环境
```bash
conda env create -f environment.yml
conda activate river
```

### 3. 初始化数据库
运行以下命令初始化 SQLite 数据库：
```bash
sqlite3 river_network.db < init_schema.sql
```

### 4. 启动 Flask 后端
```bash
python app.py
```

### 5. 启动前端
前端是一个简单的 HTML 页面，位于项目根目录下的 `index.html` 文件中。你可以直接用浏览器打开它，或者将其托管到 Flask 的静态文件目录中。

#### 方法 1：直接打开
双击 `index.html` 文件，用浏览器打开。

#### 方法 2：通过 Flask 托管
将 `index.html` 放入 Flask 的 `static` 目录中，然后通过后端访问：
```bash
http://127.0.0.1:5001/static/index.html
```

### 6. 打开浏览器
访问 `http://127.0.0.1:5001`，使用前端界面上传视频并查看分析结果。

## 贡献
欢迎提交 Issue 或 Pull Request 来改进项目！

## 许可证
本项目基于 [MIT License](LICENSE) 开源。

### 更新步骤
1. 编辑项目根目录下的 README.md 文件，将上述内容替换原有内容。
2. 提交更新：
   ```bash
   git add README.md
   git commit -m "Update README with frontend details"
   git push origin main
   ```