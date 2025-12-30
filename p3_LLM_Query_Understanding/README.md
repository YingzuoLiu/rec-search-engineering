# Project 3

## LLM-Enhanced Query Understanding for Search Matching

**（聚焦：冷启动搜索场景）**

## 1️⃣ 背景 & 问题定义

**在搜索系统中，冷启动问题并不仅仅发生在 item 或 user 上，query 本身也存在严重冷启动：**

- **查询短、模糊、非结构化**
- **新 query 无历史点击 / 无统计信号**
- **语言噪声高（口语化、描述性、组合意图）**

**传统基于 词匹配或统计特征 的方法，在这些场景下往往失效。**

**本项目聚焦于：**

**如何利用轻量级 LLM / 语义编码器，提升冷启动 query 的语义理解与召回质量，同时控制系统成本。**

## 2️⃣ 三类冷启动问题 & 对策

### （1）Query Cold-Start（查询冷启动）

#### 问题

- **新 query / 低频 query**
- **无历史点击、无 query-item 共现统计**
- **TF-IDF / BM25 对描述性查询效果差**

#### 对策

- **使用 Sentence-BERT / LLM-based encoder，将 query 映射到语义空间**
- **通过语义相似度而非词重合进行召回**

### （2）Semantic Cold-Start（语义冷启动）

#### 问题

- **Query 与 item 表达形式差异大**
  - **例：**
    - **Query: "适合加班吃的清淡速食"**
    - **Item: "低脂即食鸡胸肉 120g"**
- **词面几乎无重合，但语义高度相关**

#### 对策

- **引入 Query Rewriting / Semantic Normalization**
- **将用户 query 转换为更"item-friendly"的语义表达**
- **对齐 query embedding 与 item embedding 的分布**

### （3）Data Cold-Start（数据冷启动）

#### 问题

- **真实日志不足，难以覆盖长尾 query**
- **线上 A/B 成本高，不适合频繁试错**

#### 对策

- **构造 Synthetic Queries（描述性 / 模糊 / 组合意图）**
- **用于：**
  - **离线语义召回评估**
  - **模型对极端 query 的鲁棒性分析**

## 3️⃣ 方法概览

### 技术栈

- **Python**
- **HuggingFace Transformers**
- **Sentence-BERT**

### 数据集

- **Synthetic user queries（手工 + 模板生成）**
- **Amazon item titles / descriptions**

### 核心流程

1. **构建 query 与 item 的语义表示（embedding）**
2. **对 query 进行：**
   - **语义改写（query rewriting）**
   - **表达规范化（semantic normalization）**
3. **基于向量相似度进行召回**
4. **与以下 baseline 对比：**
   - **TF-IDF**
   - **Classical embedding methods**

## 4️⃣ 实验与对比

### 对比维度

- **Semantic Recall（是否能召回"语义相关但词不重合"的 item）**
- **对模糊 / 描述性 query 的表现**
- **推理延迟与模型规模**

### 观察结果

- **在描述性、模糊 query 上，LLM-based embedding 能显著提升语义召回**
- **在高频、明确 query 上，传统方法差距不明显**
- **模型规模与 latency 呈明显 trade-off，需要谨慎选择 encoder**

## 5️⃣ 工程视角的反思与限制

**本项目刻意没有把结论写成"LLM 一定更好"，而是关注可落地性：**

- **LLM-based retrieval 在 latency-sensitive 场景下成本较高**
- **并不适合全量替换传统召回**
- **更合理的方式是：**
  - **Hybrid Retrieval**
    - **TF-IDF / BM25 处理高频明确 query**
    - **LLM embedding 处理冷启动 / 模糊 query**
  - **或作为 recall expansion / rerank 信号**
 
---
# 面试问答实战

## 1️⃣为什么不用「纯 embedding」？

因为纯 embedding 对“表达错位”的 query–item 对齐能力有限。
展开:
* 用户 query 是：
   * 口语化
   * 模糊
   * 描述性
* item 是：
   * 结构化
   * 商品语言
* 直接 embedding：
   * 相似度不稳定
* LLM 的价值：
   * 改写 / 对齐表达
   * 再交给 embedding 做相似度
     
## 2️⃣ 成本怎么控制？什么场景不用 LLM？
### 在搜索系统里：

- 高频、稳定的 query
- 统计信号充分的场景
- 对 latency 极端敏感的路径

这些问题本身是 **统计可解的**，用规则、TF-IDF、BM25 或 embedding：

- 更便宜
- 更稳定
- 更可控

👉 **这些场景我不会用 LLM。**

## LLM 只用于：

- 冷启动 query
- 模糊 / 描述性 query
- 语义错位严重的情况

### 并且：

- 不走全量
- 有 query routing
- 有 cache / TTL
- 超时直接 fallback
