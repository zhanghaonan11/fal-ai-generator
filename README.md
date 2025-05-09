# FAL.AI 文生图工具

基于FAL.AI API的图像生成工具，支持多种模型生成高质量图像并下载为JPEG格式。

## 功能特点

- 支持多种FAL.AI模型（例如flux/dev, flux-pro/v1.1等）
- 可调整图像尺寸比例（方形、竖向、横向多种选项）
- 灵活的生成选项和参数调整
- 批量生成图像（一次最多4张）
- 生成JPEG格式的高质量图像
- 支持批量下载生成的图像

## 部署方式

### 使用Docker部署

1. 拉取Docker镜像
```bash
docker pull xcafe/fal-ai-generator:latest
```

2. 运行容器
```bash
docker run -d -p 7860:7860 -v /path/to/save/images:/app/generated_images xcafe/fal-ai-generator:latest
```

### 在1Panel中部署

1. 登录1Panel管理面板
2. 转到"应用管理" -> "Docker应用"
3. 点击"添加容器"
4. 填写以下信息：
   - 容器名称：`fal-ai-generator`
   - 镜像名称：`xcafe/fal-ai-generator:latest`
   - 端口映射：本地端口`7860`映射到容器端口`7860`
   - 目录映射：映射一个本地目录到容器的`/app/generated_images`目录
5. 点击"创建"启动容器

## 使用方法

1. 访问 `http://你的服务器IP:7860`
2. 输入详细的图像描述（提示词）
3. 选择模型和图片比例
4. 设置要生成的图片数量
5. 可选：调整高级参数（推理步数、引导比例、安全检查器）
6. 在API设置中输入您的FAL.AI API密钥
7. 点击"生成图像"按钮
8. 图像生成后，点击"下载图片为JPEG格式"按钮下载

> 请注意：您需要有效的FAL.AI API密钥才能使用此工具。可以在 https://fal.ai 注册并获取API密钥。

## 本地开发

1. 克隆仓库：
```bash
git clone https://github.com/zhanghaonan11/fal-ai-generator.git
cd fal-ai-generator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python fal_ai_image_generator.py
```

## 自定义Docker镜像

如果您想构建自己的Docker镜像：

1. 克隆仓库并进入目录
2. 构建镜像：
```bash
docker build -t your-username/fal-ai-generator .
```

3. 运行自定义镜像：
```bash
docker run -d -p 7860:7860 -v /path/to/save/images:/app/generated_images your-username/fal-ai-generator
```

## 许可证

MIT 