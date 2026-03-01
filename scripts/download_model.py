import os
from modelscope import snapshot_download

def download_qwen_emb():
    # 定义下载路径（相对于项目根目录）
    model_dir = os.path.join(os.getcwd(), "models")
    
    print("🚀 正在从 ModelScope 下载 Qwen3-Embedding-0.6B 模型...")
    try:
        snapshot_download(
            'qwen/Qwen3-Embedding-0.6B', 
            cache_dir=model_dir
        )
        print(f"✅ 模型已成功下载至: {model_dir}")
    except Exception as e:
        print(f"❌ 下载失败: {e}")

if __name__ == "__main__":
    download_qwen_emb()
