FROM python:3.9-slim

WORKDIR /app

# 安装基础工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 分步安装依赖，指定确切版本
COPY requirements.txt .
RUN pip install --no-cache-dir -v requests==2.28.2
RUN pip install --no-cache-dir -v pillow==9.4.0
RUN pip install --no-cache-dir -v fal-client==0.0.23
RUN pip install --no-cache-dir -v gradio==3.41.0

# 复制应用文件
COPY fal_ai_image_generator.py .

# 创建目录用于保存生成的图片
RUN mkdir -p /app/generated_images

EXPOSE 7860

CMD ["python", "fal_ai_image_generator.py"] 