FROM python:3.9-slim

WORKDIR /app

# 安装基础工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY fal_ai_image_generator.py .

# 创建目录用于保存生成的图片
RUN mkdir -p /app/generated_images

EXPOSE 7860

CMD ["python", "fal_ai_image_generator.py"] 