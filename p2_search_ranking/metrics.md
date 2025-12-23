# metrics.md — NDCG / Recall@K（Search & Ranking）

> 目标：用离线指标衡量「候选召回是否覆盖」以及「排序是否把相关结果排在前面」。
> 常见组合：Recall@K（看覆盖） + NDCG@K（看排序质量）。

---

## 1. 评估对象与输入

对每个 query / session（一次搜索或一次意图）：
- 系统输出一个 Top-K 排序列表：`ranked_items[1..K]`
- 有一个 ground truth 相关集合（或相关等级）：
  - Binary relevance：相关=1，不相关=0（最常见）
  - Graded relevance：比如 {0,1,2,3} 表示弱相关/强相关（更贴近真实）

**注意：** Search 里 ground truth 常来自点击/购买/加购等行为，需要做去噪（比如去掉误触、位置偏差校正）。

---

## 2. Recall@K（召回覆盖指标）

### 2.1 定义（每个 query）
Recall@K 衡量：**Top-K 里命中了多少“应当命中”的相关结果**。

- 设 `GT` 为该 query 的相关集合，`|GT| > 0`
- 设 `TopK` 为模型输出的前 K 个结果

\[
Recall@K = \frac{|TopK \cap GT|}{|GT|}
\]

### 2.2 直觉
- Recall@K 高：说明召回/候选阶段“没漏掉”用户可能喜欢的东西（覆盖好）
- Recall@K 低：说明候选列表里缺货（后面排序再强也救不了）

### 2.3 什么时候用它
- 重点看 **recall stage / candidate retrieval**（例如 ANN / Dual-Encoder / LightGCN）
- 也可以用来衡量 “粗排之后还剩多少相关”（例如 Top200 → Top50 的保留率）

### 2.4 常见坑
- **|GT| 很大/很小** 会导致可比性差：Ground Truth 很小（比如只有1个正样本）时，Recall@K 更像 Hit@K
- **负样本不参与**：Recall@K 不关心不相关排得多靠前（所以它不是排序指标）

---

## 3. NDCG@K（排序质量指标）

### 3.1 为什么需要 NDCG
Recall@K 只关心“有没有命中”，不关心“排得靠不靠前”。  
Search/Rank 更关心：**越相关越靠前**，因为用户通常只看前几条。

### 3.2 DCG@K（Discounted Cumulative Gain）
对于位置 i（从 1 开始），相关性为 `rel_i`（可以是0/1，也可以是等级）。

常用的 DCG 定义之一：
\[
DCG@K = \sum_{i=1}^{K} \frac{2^{rel_i}-1}{\log_2(i+1)}
\]

- 分子：相关性越高贡献越大（graded relevance 时更明显）
- 分母：位置折损，越靠后权重越小（体现“前排更重要”）

### 3.3 IDCG@K（Ideal DCG）
把该 query 的结果按相关性从高到低“完美排序”，得到最大可能的 DCG：
\[
IDCG@K = DCG@K(\text{ideal ranking})
\]

### 3.4 NDCG@K（归一化）
\[
NDCG@K = \frac{DCG@K}{IDCG@K}
\]
范围在 [0, 1]（通常），更容易跨 query 对比。

### 3.5 直觉
- NDCG@K 高：相关结果不仅出现了，还集中在前面
- NDCG@K 低：可能 Recall 还可以，但相关结果被排到后面了

### 3.6 常见坑
- **IDCG 为 0 的 query**（该 query 没有任何相关标签）：要么过滤掉，要么规定 NDCG=0（推荐过滤，否则指标会被噪声影响）
- **Binary relevance 时**，NDCG 会更“粗”，graded relevance 更能体现强弱相关差异
- **K 的选择**：Search 常看 NDCG@10/20（贴近用户可见范围）

---

## 4. 怎么汇报指标（面试向）

### 4.1 推荐汇报格式
- Retrieval：Recall@50 / Recall@100（候选覆盖）
- Ranking：NDCG@10 / NDCG@20（前排质量）

示例（模板）：
- “Recall@100 从 0.62 → 0.70，说明候选覆盖更好；同时 NDCG@10 从 0.34 → 0.39，说明相关结果更靠前。”

### 4.2 如果 Recall 提升但 NDCG 没提升
可能原因：
- 新召回补进来的相关结果被 rank 模型打分偏低（特征缺失 / 分布不一致）
- rank 目标与评估不一致（优化点击却评估相关性）
- 训练数据偏差（曝光偏差、位置偏差）

### 4.3 如果 NDCG 提升但线上 CTR 不涨
典型追问点：
- 离线标签与线上目标不一致（比如 NDCG 用 click=rel，但线上更关心 purchase）
- A/B 实验口径差异（分桶、冷启动、流量混合）
- 线上干预（重排规则、过滤、库存、价格等）改变了最终曝光列表

---

## 5. 实用实现细节（工程角度）

### 5.1 多 query 的聚合方式
最常见：对每个 query 先算指标，再取平均：
- Macro average：`mean(metric_per_query)`（推荐，避免大 query 垄断）
- Micro average：把所有命中合并再算（容易被头部 query 主导）

### 5.2 K 的选择建议
- Recall：K 取候选规模（50/100/200）
- NDCG：K 取用户可见范围（10/20）

---

## 6. 什么时候我会选 Recall 而不是 NDCG？
- 你在做“召回模块”（embedding/ANN）时：Recall@K 是第一优先
- 你在做“排序模型”（ranker）时：NDCG@K 更敏感、更符合产品体验

---
