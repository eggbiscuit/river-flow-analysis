-- 创建 video 表，记录视频信息
CREATE TABLE IF NOT EXISTS video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    uploaded_at TEXT NOT NULL
);

-- 创建 node 表，记录视频中的区域节点信息
CREATE TABLE IF NOT EXISTS node (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER,
    region_x INTEGER NOT NULL,
    region_y INTEGER NOT NULL,
    region_width INTEGER NOT NULL,
    region_height INTEGER NOT NULL,
    flow_speed REAL NOT NULL,
    flow_direction TEXT NOT NULL,
    max_speed REAL NOT NULL, -- 添加最大速度字段
    timestamp TEXT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES video(id)
);

-- 创建 edge 表，记录水流连接关系（有向图）
CREATE TABLE IF NOT EXISTS edge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node INTEGER,
    to_node INTEGER,
    distance REAL NOT NULL,
    FOREIGN KEY (from_node) REFERENCES node(id),
    FOREIGN KEY (to_node) REFERENCES node(id)
);