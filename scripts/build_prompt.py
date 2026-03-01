import sys, os, json, subprocess

def get_skill_content():
    with open('/root/.openclaw/skills/elderly-copywriter/SKILL.md', 'r', encoding='utf-8') as f:
        return f.read()

def get_rag_template(topic):
    # 调用之前的检索脚本
    result = subprocess.run(
        ['python3.11', '/root/.openclaw/scripts/match_template.py', topic],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def build_generate_prompt(topic, opinion):
    skill = get_skill_content()
    template = get_rag_template(topic)
    return f"""
请严格阅读并遵循下方的【SKILL 手册】执行创作。

[SKILL_START]
{skill}
[SKILL_END]

[TEMPLATE_START]
以下是供你参考的高赞爆款 JSONL 范文：
{template}
[TEMPLATE_END]

本次创作任务如下：
- 核心主题：{topic}
- 核心观点：{opinion}

请开始你的结构化思考并直接输出最终的 JSON 对象：
"""

def build_refine_prompt(feedback):
    # 读取当前文章
    try:
        with open('/root/.openclaw/latest_article.json', 'r', encoding='utf-8') as f:
            current = f.read()
    except:
        current = "{}"
        
    skill = get_skill_content()
    return f"""
请参考以下【SKILL 手册】的标准结构：
[SKILL_START]
{skill}
[SKILL_END]

原推文数据：
{current}

修改意见："{feedback}"。
请根据意见修改，必须严格按照 SKILL 手册结构重新输出 JSON。
"""

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "generate":
        print(build_generate_prompt(sys.argv[2], sys.argv[3]))
    elif mode == "refine":
        print(build_refine_prompt(sys.argv[2]))
