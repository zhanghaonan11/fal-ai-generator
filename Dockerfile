FROM python:3.9-slim

WORKDIR /app

# 安装基础工具和必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip和安装基础工具
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 分步安装依赖以便于调试
COPY requirements.txt .
RUN pip install --no-cache-dir -v requests==2.31.0
RUN pip install --no-cache-dir -v pillow==9.5.0
RUN pip install --no-cache-dir -v gradio==3.41.0
RUN pip install --no-cache-dir -v fal-client==0.1.13

# 复制应用文件
COPY fal_ai_image_generator.py .

# 创建目录用于保存生成的图片
RUN mkdir -p /app/generated_images

EXPOSE 7860

CMD ["python", "fal_ai_image_generator.py"] 