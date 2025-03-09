import gradio as gr
import os
import json
from PIL import Image
import io
import base64
import fal_client
import time
import requests
from fal_client import FalClient

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
    
    # 设置API密钥
    os.environ["FAL_KEY"] = api_key
    
    try:
        client = FalClient()
        images = []
        image_paths = []  # 存储图片保存路径
        
        # 准备API请求
        model_url = f"https://110602490-sdxl-turbo.gateway.alpha.fal.ai"
        if model_id == "stability":
            model_url = f"https://110602490-stability-image-generation.gateway.alpha.fal.ai"
        elif model_id == "dalle3":
            model_url = f"https://110602490-dalle-3.gateway.alpha.fal.ai"
            
        # 准备请求参数
        request_params = {
            "prompt": prompt,
            "num_images": int(num_images),
            "aspect_ratio": aspect_ratio
        }
        
        if model_id == "sdxl":
            request_params["steps"] = int(num_steps)
            request_params["guidance_scale"] = float(guidance)
            request_params["enable_safety_checker"] = safety_checker == "启用"
            
        # 提交请求
        print(f"发送请求到 {model_url}")
        print(f"请求参数: {request_params}")
        
        # 用于存储最终结果
        result = None
        
        # 定义队列更新回调函数
        def on_queue_update(update):
            nonlocal result
            print(f"队列更新: {update}")
            status = update.get("status")
            if status == "COMPLETED":
                result = update.get("result", {})
                print(f"生成完成，获取结果")
        
        # 发送请求
        client.submit_request(
            model_url, 
            request_params, 
            on_queue_update=on_queue_update,
            timeout=300  # 5分钟超时
        )
        
        # 处理返回结果
        if "images" in result:
            # 创建保存图片的目录
            save_dir = "generated_images"
            os.makedirs(save_dir, exist_ok=True)
            
            for i, img_data in enumerate(result["images"]):
                if "url" in img_data:
                    # 加载图片URL
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
        if not images:
            return "未能生成图像，请检查提示词或重试", None, None
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
    gr.Markdown("# 🎨 FAL.AI 文生图工具")
    gr.Markdown("使用FAL.AI API生成高质量图像")
    
    # 创建API密钥输入框
    api_key = gr.Textbox(label="FAL.AI API密钥", type="password", placeholder="输入你的FAL.AI API密钥")
    
    # 存储图片路径的状态变量
    image_paths_state = gr.State([])
    
    with gr.Row():
        with gr.Column():
            # 创建模型选择下拉框
            model = gr.Dropdown(
                label="选择模型",
                choices=["sdxl", "stability", "dalle3"],
                value="sdxl",
                interactive=True
            )
            
            # 创建输入框
            prompt = gr.Textbox(label="提示词 (Prompt)", placeholder="描述你想要生成的图像...", lines=3)
            
            # 创建配置选项
            with gr.Group():
                num_images = gr.Slider(minimum=1, maximum=4, value=1, step=1, label="生成图像数量")
                aspect_ratio = gr.Dropdown(
                    label="宽高比",
                    choices=["square", "portrait", "landscape"],
                    value="square",
                    interactive=True
                )
                
                # SDXL特有的选项
                with gr.Group(visible=True) as sdxl_options:
                    num_steps = gr.Slider(minimum=1, maximum=50, value=25, step=1, label="推理步数")
                    guidance = gr.Slider(minimum=1.0, maximum=20.0, value=7.5, step=0.1, label="提示词引导强度")
                    safety_checker = gr.Radio(choices=["启用", "禁用"], value="启用", label="安全检查")
            
            # 创建生成按钮
            generate_btn = gr.Button("生成图像", variant="primary")
        
        with gr.Column():
            output_message = gr.Textbox(label="状态消息")
            output_gallery = gr.Gallery(label="生成的图像", columns=2)
            download_btn = gr.Button("下载图片为JPEG格式", visible=False)
            download_output = gr.File(label="下载链接", visible=False)
    
    # 更新模型选择时显示/隐藏相关选项
    def update_model_options(model_name):
        return gr.update(visible=model_name == "sdxl")
    
    model.change(
        fn=update_model_options,
        inputs=[model],
        outputs=[sdxl_options]
    )
    
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

# 启动应用
if __name__ == "__main__":
    import sys
    import subprocess
    
    # 检查并安装必要的依赖
    required_packages = ["fal-client", "pillow", "gradio"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"安装依赖包: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # 启动Gradio应用
    demo.launch(server_name="0.0.0.0", share=False) 
    demo.launch() 