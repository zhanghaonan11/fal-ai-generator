FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fal_ai_image_generator.py .

# 创建目录用于保存生成的图片
RUN mkdir -p /app/generated_images

EXPOSE 7860

CMD ["python", "fal_ai_image_generator.py"] 