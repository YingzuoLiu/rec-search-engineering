## 多路召回结果合并

### 题目

合并 TF-IDF 和 LLM 的召回结果，要求：

- 去重
- 保序（TF-IDF 优先）
- 只返回 Top K

```python
def merge_results(tfidf, llm, k):
    seen = set()
    result = []

    for item in tfidf:
        if item not in seen:
            seen.add(item)
            result.append(item)
            if len(result) == k:
                return result

    for item in llm:
        if item not in seen:
            seen.add(item)
            result.append(item)
            if len(result) == k:
                return result

    return result
```
## Query Normalization

### 题目

对用户 query 做基础规范化处理。

```python
def normalize_query(query: str) -> str:
    """
    - lowercase
    - 去多余空格
    - 同义词映射
    """
    synonym = {
        "cheap": "low price",
        "fast": "quick",
    }

    q = query.lower().strip()
    words = q.split()

    normalized = []
    for w in words:
        normalized.append(synonym.get(w, w))

    return " ".join(normalized)
```
