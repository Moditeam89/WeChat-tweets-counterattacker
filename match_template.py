import sys, numpy as np, json
from sentence_transformers import SentenceTransformer

# 全局模型单例
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('/root/.openclaw/models/qwen/Qwen3-Embedding-0.6B', device='cpu')
    return _model

def get_best(kw):
    model = get_model()
    with open('/root/.openclaw/templates/elderly_templates.txt', 'r', encoding='utf-8') as f:
        lines =[l.strip() for l in f if l.strip()]
        
    texts_for_encoding =[]
    for line in lines:
        try:
            data = json.loads(line)
            texts_for_encoding.append(data.get("title", "") + " " + data.get("content", ""))
        except:
            texts_for_encoding.append(line)
            
    vecs = model.encode(texts_for_encoding)
    kw_vec = model.encode([kw])[0]
    scores =[np.dot(kw_vec, v) / (np.linalg.norm(kw_vec) * np.linalg.norm(v)) for v in vecs]
    return lines[np.argmax(scores)]

if __name__ == "__main__":
    # 处理可能的标准输入编码问题
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(get_best(sys.argv[1]))
