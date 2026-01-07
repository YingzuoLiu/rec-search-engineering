# Fallback & Guardrail --- 回顾速查

**（Multimodal Cold-Start Retrieval）**

## 1️⃣ 用户视角的完整流程

### 用户只做一件事

- **搜索一个词（text query）**
- **或点进一个商品（相似推荐）**

**👉 用户只关心：这一页结果看起来正不正常**

### 系统背后的真实流程

```
用户行为
↓
Query encoder（文本）
↓
FAISS 检索（item 是多模态 embedding）
↓
结果质量自检（fallback / guardrail）
↓
最终展示
```

### ⚠️ 关键点

- **Query 本身不是多模态**
- **多模态在 item 侧（image + text）**

## 2️⃣ 什么是 fallback？什么时候触发？

### ❌ 不是判断「用了什么模型」

### ✅ 是判断「这页结果靠不靠谱」

**系统不问：**

**"我是不是用多模态？"**

**系统问：**

**"我敢不敢把这一页直接给用户？"**

## 3️⃣ fallback 的核心判断：看 cosine 分布（不是单值）

### 使用的相似度

- **cosine similarity**
- **工程里常简写为 sim / score**

### ✅ 三个最常用的分布级判断

#### 1️⃣ 平均相似度太低（整体不相关）

```python
mean(cos_scores) < 0.25
→ fallback
```

**直觉：**

**整页都不太像，别硬推。**

#### 2️⃣ 区分度不足（分不出谁更好）

```python
top1_cos - mean_cos < 0.05
→ fallback
```

**直觉：**

**embedding 在"猜"，不是在"判断"。**

#### 3️⃣（可选）分布过于集中

```python
std(cos_scores) 很小
→ fallback
```

**直觉：**

**所有 item 都差不多，没判断力。**

### ✅ 标准工程版判断函数

```python
def should_fallback(cos_scores):
    if not cos_scores:
        return True
    
    mean_cos = np.mean(cos_scores)
    gap = cos_scores[0] - mean_cos
    
    if mean_cos < 0.25:
        return True
    
    if gap < 0.05:
        return True
    
    return False
```

## 4️⃣ fallback 走哪条路？

### 分层兜底（非常工程）

```
Multimodal recall
↓（质量不行）
Text-only recall
↓
Popularity / rule recall
```

**目标不是"最准"，而是：**

**永远有结果，而且不奇怪**

## 5️⃣ 什么是 guardrail？（和 fallback 的区别）

| **fallback** | **guardrail** |
|--------------|---------------|
| **换一条路** | **在当前结果里"修一修"** |
| **解决"有没有结果"** | **解决"结果会不会离谱"** |

### 常见 guardrail

- **同 brand 数量限制（避免刷屏）**
- **新商品比例限制（冷启动保护）**
- **过滤极低 cosine 的 item**

## 6️⃣ 三个关键工程概念

### 1️⃣ scores / ids / items 是什么？

- **scores：cosine similarity（像不像）**
- **ids：item ID（是谁）**
- **items：真正的商品对象（title / brand / is_new）**

```python
scores, ids = index.search(query_vec, k)
retrieved_items = [items[i] for i in ids]
```

### 2️⃣ 为什么不用单一 cosine 阈值？

**❌ score > 0.3  
→ 容易误杀冷启动 / 模糊 query**

**✅ 看 Top-K 整体分布  
→ 判断"这一页值不值得给用户"**

### 3️⃣ fallback ≠ 剪掉结果

**错误做法：**

**不满足阈值 → 直接丢**

**正确做法：**

**质量不够 → 换一条更稳的召回路径**

## 7️⃣ Living coding 最常考什么（项目四相关）

### ⭐ 必考 1：多路召回合并 + 去重

```python
def merge_recalls(recall_lists, max_n):
    seen = set()
    result = []
    
    for lst in recall_lists:
        for item in lst:
            if item.id in seen:
                continue
            seen.add(item.id)
            result.append(item)
            if len(result) >= max_n:
                return result
    
    return result
```

### ⭐ 必考 2：质量判断 + fallback

```python
if should_fallback(cos_scores):
    return fallback_recall()
```
