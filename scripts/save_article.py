import sys, json, re

def safe_json_parse(text):
    # 清洗 Markdown 标记
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    clean_text = match.group(1) if match else text
    return json.loads(clean_text.strip())

if __name__ == "__main__":
    # 从命令行参数获取 LLM 输出
    raw_output = sys.argv[1]
    
    try:
        data = safe_json_parse(raw_output)
        # 逻辑缝合：Hook + Body + Closing -> Content
        final_content = f"{data.get('hook', '')}\n\n{'\n\n'.join(data.get('body', []))}\n\n{data.get('closing', '')}"
        
        save_data = {
            "title": data.get("title", "无标题"),
            "content": final_content,
            "meta": data.get("meta", {})
        }
        
        with open('/root/.openclaw/latest_article.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 草稿已保存！\n📌 标题：{save_data['title']}\n📝 正文摘要：{final_content[:50]}...")
        print("\n👉 下一步：输入 /微调 <意见> 修改，或输入 /发布微信 推送。")
        
    except Exception as e:
        print(f"❌ 保存失败，JSON 格式错误：{e}")
        print("原始输出：", raw_output[:100])
