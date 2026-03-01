import json, os, requests, concurrent.futures
from dotenv import load_dotenv

load_dotenv('/root/.openclaw/.env')
DEFAULT_COVER = "/root/.openclaw/assets/default_cover.jpg"

def get_token():
    r = requests.get(
        f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={os.getenv('WECHAT_APPID')}&secret={os.getenv('WECHAT_APPSECRET')}"
    )
    return r.json()["access_token"]

def get_cover_and_inner_images():
    """根据主题返回封面和内页图URL列表"""
    try:
        with open('/root/.openclaw/latest_article.json', 'r', encoding='utf-8') as f:
            article = json.load(f)
        title = article.get('title', '')
    except:
        title = ''
    
    # 根据标题关键词匹配封面和内页图
    if '马拉松' in title:
        return {
            "cover": [
                "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=900&h=383&fit=crop",
                "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=900&h=383&fit=crop",
            ],
            "inner1": [
                "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800&h=600&fit=crop",
            ],
            "inner2": [
                "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&h=600&fit=crop",
            ]
        }
    elif '热水' in title or '喝水' in title or '养生' in title or '健康' in title:
        return {
            "cover": [
                "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=900&h=383&fit=crop",
                "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=900&h=383&fit=crop",
            ],
            "inner1": [
                "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800&h=600&fit=crop",
            ],
            "inner2": [
                "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=800&h=600&fit=crop",
            ]
        }
    else:
        # 默认风景
        return {
            "cover": [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=900&h=383&fit=crop",
                "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=900&h=383&fit=crop",
            ],
            "inner1": [
                "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&h=600&fit=crop",
            ],
            "inner2": [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
            ]
        }

def search_and_download_image(keyword, size, filename):
    """下载图片 - 根据主题自动匹配"""
    save_path = f"/root/.openclaw/assets/{filename}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 获取对应类型的图片URL列表
    images = get_cover_and_inner_images()
    
    if filename == "cover.jpg":
        urls = images.get("cover", images.get("inner1", []))
    elif filename == "inner1.jpg":
        urls = images.get("inner1", images.get("inner2", []))
    elif filename == "inner2.jpg":
        urls = images.get("inner2", images.get("inner1", []))
    else:
        keyword_images = {
            "荷花": [
                "https://images.unsplash.com/photo-1518882605630-8eb582dd4e5f?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1579520143486-450a7b3451bb?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1585336261022-680e295ce3fe?w=800&h=600&fit=crop",
            ],
            "莲花": [
                "https://images.unsplash.com/photo-1579520143486-450a7b3451bb?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1518882605630-8eb582dd4e5f?w=800&h=600&fit=crop",
            ],
            "风景": [
                "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
            ],
            "山水": [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&h=600&fit=crop",
            ],
        }
        urls = keyword_images.get(keyword, keyword_images.get("风景"))
    
    # 尝试下载
    for url in urls:
        try:
            r = requests.get(url, timeout=30, headers=headers)
            if r.status_code == 200 and len(r.content) > 5000:
                with open(save_path, "wb") as f:
                    f.write(r.content)
                print(f"✅ 下载成功: {filename}")
                return save_path
        except Exception as e:
            print(f"⚠️ 下载失败: {url}, {e}")
            continue
    
    print(f"❌ 使用默认图: {filename}")
    return DEFAULT_COVER

def publish():
    token = get_token()
    
    if not os.path.exists(DEFAULT_COVER):
        print("❌ 严重错误：保底图不存在")
        return

    with open('/root/.openclaw/latest_article.json', 'r', encoding='utf-8') as f:
        article = json.loads(f.read())

    # 下载图片
    print("🔍 下载图片...")
    tasks = [
        ("cover", "900x383", "cover.jpg"),        
        ("荷花", "800x600", "inner1.jpg"),        
        ("山水", "800x600", "inner2.jpg"),        
    ]
    
    img_paths = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(search_and_download_image, t[0], t[1], t[2]): t[2] for t in tasks}
        for future in concurrent.futures.as_completed(futures):
            img_paths[futures[future]] = future.result()

    # 上传封面
    print("📤 上传封面...")
    cover_file = img_paths.get("cover.jpg") or DEFAULT_COVER
    with open(cover_file, "rb") as f:
        files = {"media": ("cover.jpg", f, "image/jpeg")}
        r = requests.post(
            f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
            files=files
        )
    thumb_id = r.json()["media_id"]
    print(f"封面上传成功: {thumb_id}")

    # 上传正文图片
    print("📤 上传正文图片...")
    inline_urls = []
    for key in ["inner1.jpg", "inner2.jpg"]:
        path = img_paths.get(key)
        if path and os.path.exists(path) and path != DEFAULT_COVER:
            with open(path, "rb") as f:
                files = {"media": (key, f, "image/jpeg")}
                r = requests.post(
                    f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
                    files=files
                )
            if "url" in r.json():
                inline_urls.append(r.json()["url"])
                print(f"  {key} 上传成功")

    # 构建内容 - content 字段已包含完整正文，直接使用并插入图片
    content = article["content"].replace('\n', '<br/>')
    paras = content.split('<br/>')
    new_content = []
    img_idx = 0
    for i, p in enumerate(paras):
        new_content.append(p)
        # 在第1段后插入inner1，第3段后插入inner2
        if i == 1 and img_idx < len(inline_urls):
            new_content.append(f'<p style="text-align:center;margin:15px 0"><img src="{inline_urls[img_idx]}" style="width:100%;border-radius:8px"></p>')
            img_idx += 1
        if i == 3 and img_idx < len(inline_urls):
            new_content.append(f'<p style="text-align:center;margin:15px 0"><img src="{inline_urls[img_idx]}" style="width:100%;border-radius:8px"></p>')
            img_idx += 1
    
    final_content = '<br/>'.join(new_content)
    html = f"<div style='font-size:16px;line-height:1.8;color:#333;padding:15px;'>{final_content}</div>"

    # 创建草稿
    title = article["title"]
    if len(title) > 20:
        title = title[:18] + "..."
    
    draft_data = {
        "articles": [{
            "title": title,
            "thumb_media_id": thumb_id,
            "author": "老王",
            "content": html,
            "show_cover_pic": 1
        }]
    }
    
    data = json.dumps(draft_data, ensure_ascii=False).encode('utf-8')
    r = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    print("📝 草稿创建:", r.json())

    if "media_id" in r.json():
        print("✅ 成功！请去公众号后台查看")
    else:
        print("❌ 失败:", r.json())

if __name__ == "__main__":
    publish()
