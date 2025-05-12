# 基础镜像
FROM python:3.10-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    cmake \
    g++ \
    make \
    opencv-dev

# 复制项目文件到容器中
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 构建 C++ 程序
RUN mkdir build && cd build && cmake .. && make

# 初始化数据库
RUN python scripts/init_db.py

# 暴露端口
EXPOSE 5001

# 启动服务
CMD ["python", "app.py"]