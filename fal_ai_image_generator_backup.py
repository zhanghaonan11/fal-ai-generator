import gradio as gr
import os
import io
import time
import json
import requests
from PIL import Image
import fal_client

# 默认模型和API密钥
DEFAULT_MODEL = "fal-ai/flux/dev"
MODEL_OPTIONS = [
    "fal-ai/flux/dev",
    "fal-ai/flux-pro/v1.1",
    "fal-ai/flux-pro/v1.1-ultra-finetuned"
]

# 图片比例选项 - 使用官方枚举值
ASPECT_RATIOS = {
    "1:1 (方形-高清)": "square_hd",
    "1:1 (方形-标准)": "square",
    "3:4 (竖向)": "portrait_4_3",
    "9:16 (竖向)": "portrait_16_9",
    "4:3 (横向)": "landscape_4_3",
    "16:9 (横向)": "landscape_16_9"
}

def generate_image(prompt, model_id, aspect_ratio, num_images, num_steps, guidance, safety_checker, api_key):
    """调用FAL.AI API生成图像"""
    if not api_key:
        return "请提供有效的API密钥", None, None
    
    # 暂时设置环境变量用于认证
    os.environ["FAL_KEY"] = api_key
    
    # 获取正确的枚举值
    image_size = ASPECT_RATIOS[aspect_ratio]
    
    try:
        # 使用官方客户端库调用API
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(log["message"])
        
        # 构建请求参数
        arguments = {
            "prompt": prompt,
            "image_size": image_size,
            "num_images": int(num_images)
        }
        
        # 添加可选参数
        if num_steps:
            arguments["num_inference_steps"] = int(num_steps)
        
        if guidance:
            arguments["guidance_scale"] = float(guidance)
            
        if safety_checker is not None:
            arguments["enable_safety_checker"] = safety_checker
        
        # 执行API调用
        result = fal_client.subscribe(
            model_id,
            arguments=arguments,
            with_logs=True,
            on_queue_update=on_queue_update
        )
        
        # 处理返回结果
        images = []
        image_paths = []  # 存储图片保存路径
        
        if "images" in result:
            # 创建保存图片的目录
            save_dir = "generated_images"
            os.makedirs(save_dir, exist_ok=True)
            
            for i, img_data in enumerate(result["images"]):
                if "url" in img_data:
                    # 加载图片URL
                    import requests
                    img_response = requests.get(img_data["url"])
                    img = Image.open(io.BytesIO(img_response.content))
                    
                    # 确保图片是RGB模式（移除透明通道）
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 保存为JPEG
                    timestamp = int(time.time())
                    filename = f"{save_dir}/image_{timestamp}_{i+1}.jpg"
                    img.save(filename, format="JPEG", quality=95)
                    image_paths.append(filename)
                    
                    # 为显示保留PIL图像对象
                    images.append(img)
        
        # 返回增加了图片路径
        return "图像生成成功！", images, image_paths
    except Exception as e:
        return f"生成图像时出错: {str(e)}", None, None
    finally:
        # 清除环境变量
        if "FAL_KEY" in os.environ:
            del os.environ["FAL_KEY"]

# 添加下载图片的函数
def download_images(image_paths):
    if not image_paths or len(image_paths) == 0:
        return "没有可下载的图片"
    
    # 如果只有一张图片，直接返回路径
    if len(image_paths) == 1:
        return image_paths[0]
    
    # 如果有多张图片，打包成zip文件
    import zipfile
    zip_filename = f"generated_images_{int(time.time())}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for img_path in image_paths:
            if os.path.exists(img_path):
                zipf.write(img_path, os.path.basename(img_path))
    
    return zip_filename

# 创建Gradio界面
with gr.Blocks(title="FAL.AI 文生图工具") as demo:
    gr.Markdown("# FAL.AI 文生图工具")
    gr.Markdown("使用FAL.AI的模型从文本生成图像")
    
    # 添加存储图片路径的状态变量
    image_paths_state = gr.State([])
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="提示词", placeholder="输入详细的图像描述...", lines=3)
            model = gr.Dropdown(choices=MODEL_OPTIONS, value=DEFAULT_MODEL, label="选择模型")
            aspect_ratio = gr.Dropdown(choices=list(ASPECT_RATIOS.keys()), value="4:3 (横向)", label="图片比例")
            num_images = gr.Number(value=1, minimum=1, maximum=4, step=1, label="图片数量")
            
            with gr.Accordion("高级设置", open=False):
                num_steps = gr.Number(value=28, minimum=1, maximum=50, step=1, label="推理步数")
                guidance = gr.Number(value=3.5, minimum=1.0, maximum=20.0, step=0.1, label="引导比例")
                safety_checker = gr.Checkbox(value=True, label="启用安全检查器")
            
            with gr.Accordion("API设置", open=False):
                api_key = gr.Textbox(label="API Key", type="password")
            
            generate_btn = gr.Button("生成图像")
        
        with gr.Column():
            output_message = gr.Textbox(label="状态消息")
            output_gallery = gr.Gallery(label="生成的图像", columns=2)
            download_btn = gr.Button("下载图片为JPEG格式", visible=False)
            download_output = gr.File(label="下载链接", visible=False)
    
    # 更新生成按钮的处理函数
    generate_btn.click(
        fn=generate_image,
        inputs=[prompt, model, aspect_ratio, num_images, num_steps, guidance, safety_checker, api_key],
        outputs=[output_message, output_gallery, image_paths_state]
    ).then(
        fn=lambda x: gr.update(visible=True) if x else gr.update(visible=False),
        inputs=[image_paths_state],
        outputs=[download_btn]
    )
    
    # 下载按钮的处理函数
    download_btn.click(
        fn=download_images,
        inputs=[image_paths_state],
        outputs=[download_output]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=[download_output]
    )
    
    gr.Markdown("""
    ## 使用说明
    1. 输入详细的图像描述（提示词）
    2. 选择模型和图片比例
    3. 设置要生成的图片数量
    4. 可选：调整高级参数（推理步数、引导比例、安全检查器）
    5. 在API设置中输入您的FAL.AI API密钥
    6. 点击"生成图像"按钮
    
    请注意：您需要有效的FAL.AI API密钥才能使用此工具。
    可以在 https://fal.ai 注册并获取API密钥。
    """)

# 启动应用
if __name__ == "__main__":
    # 安装必要的依赖
    import sys
    import subprocess
    required_packages = ["fal-client", "pillow", "gradio"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"安装依赖包: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    demo.launch() 