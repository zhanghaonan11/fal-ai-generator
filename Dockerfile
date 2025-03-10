FROM python:3.9-slim

WORKDIR /app

# 安装基础工具和必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 升级pip和安装基础工具
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 分步安装核心依赖
COPY requirements.txt .
RUN pip install --no-cache-dir requests==2.31.0
RUN pip install --no-cache-dir pillow==9.5.0
RUN pip install --no-cache-dir gradio==3.41.0
RUN pip install --no-cache-dir fal-client

# 复制应用文件
COPY fal_ai_image_generator.py .

# 创建目录用于保存生成的图片
RUN mkdir -p /app/generated_images

# 设置环境变量
ENV PORT=7860
ENV HOST=0.0.0.0
ENV SAVE_DIR=/app/generated_images

# 暴露端口
EXPOSE 7860

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# 启动应用
CMD ["python", "fal_ai_image_generator.py"]