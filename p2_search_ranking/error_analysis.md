# Representative Failure Cases in Search & Ranking System

**本文件记录在离线评估与人工检查过程中发现的典型失败样例，  
目的是理解系统行为边界，而非追求指标上的极端优化。**

## Case 1：Query 语义歧义导致 Intent 偏移

### Query
**"spicy noodles"**

### Top-5 Returned Results
1. **Instant Cup Noodles (Mild)**
2. **Instant Cup Noodles (Seafood)**
3. **Instant Ramen Pack**
4. **Chili Sauce**
5. **Bowl Set**

### 期望行为（人工判断）
- **更偏向 辣味拉面 / 辣汤面**
- **而非 "方便面 + 口味弱相关商品"**

### 问题定位
- **Query 语义被模型理解为"noodles"主导**
- **"spicy" 权重不足**
- **排名更受 item popularity 影响**

### 错误类型
- **Query / Intent Error**
- **Ranking 被 popularity bias 主导**

### 当前结论
- **这是 语义细粒度不足 的典型 case**
- **不属于 recall miss，而是 ranking 方向偏移**

---

## Case 2：Relevant Item 未被召回（Recall Miss）

### Query
**"korean spicy ramen"**

### Ground Truth（点击 / 人工相关）
**Samyang Hot Chicken Ramen**

### Recall Candidates（Top-100）
**❌ GT item 不在 recall list 中**

### 问题定位
- **Ranking 模型未介入（无候选）**
- **问题发生在 recall 阶段**

### 可能原因
- **Query embedding 与 item embedding 未对齐**
- **向量召回对品牌词敏感度不足**
- **ANN 搜索精度设置偏保守**

### 错误类型
- **Recall Error（Recall Miss）**

### 当前结论
- **Ranking 再强也无法修复**
- **属于 recall coverage 问题**

---

## Case 3：Recall 正确，但排序靠后

### Query
**"low sugar snacks"**

### Recall Candidates（简化）
- **Rank 1-3: Popular Cookies (High Sugar)**
- **Rank 4: Low Sugar Protein Bar ← GT**
- **Rank 5: Low Sugar Biscuits**

### 现象
- **GT item 已被召回**
- **但排在 rank 4，未进入 Top-3**

### 问题定位
- **排序方向基本正确**
- **但 特征区分度不足**

### 可能原因
- **Ranking 特征偏重点击率 / 热度**
- **"low sugar" 属性权重不够**

### 错误类型
- **Ranking Error（Under-ranked Relevant Item）**

### 当前结论
- **属于 Top-K 精排问题**
- **可通过特征增强或 loss 调整改善**

---

## Case 4：长尾 Query 召回不足（Sparse Query）

### Query
**"vegan gluten free snacks"**

### Recall Size
**< 10 items**

### 现象
- **Ranking 可选空间极小**
- **返回结果相关性整体一般**

### 问题定位
- **Query 过长、语义过细**
- **数据中对应 item 极少**

### 错误类型
- **Query Sparsity / Recall Coverage**

### 当前结论
- **属于数据与需求不匹配**
- **可通过 fallback 或 query 放宽处理**

---

## Case 5：热门商品"看起来合理，但不对用户"

### Query
**"healthy breakfast"**

### Top Results
1. **Best-selling Cereal**
2. **Popular Granola**
3. **Instant Oats**

### 人工判断
- **结果整体合理**
- **但 缺乏个性化 / 多样性**
- **用户偏好可能被忽略**

### 问题定位
- **排序高度依赖历史点击**
- **个性化特征权重不足**

### 错误类型
- **Ranking Bias（Popularity-dominated）**

### 当前结论
- **离线指标不一定下降**
- **但用户体验存在风险**

---

## Error Case 总结表（简化）

| **Case** | **阶段** | **错误类型** |
|----------|----------|--------------|
| **1** | **Query / Rank** | **Intent Mismatch** |
| **2** | **Recall** | **Recall Miss** |
| **3** | **Rank** | **Under-ranked GT** |
| **4** | **Query / Recall** | **Sparse Query** |
| **5** | **Rank** | **Popularity Bias** |

---

## 项目层面的结论

- **大多数失败并非单点 bug**
- **而是 Query / Recall / Ranking 边界自然暴露**
- **Error analysis 的价值在于：**
  - **明确"哪一层该背锅"**
  - **避免盲目堆模型复杂度**

## 面试时你可以这样总结

**"我在项目中会把失败 case 按 Query、Recall、Ranking 拆分分析，很多时候问题并不是模型不够复杂，而是语义边界、数据覆盖或阶段职责不清。"**

---
# Error Analysis for Session-based Sequence Recommendation (DIN-style Attention)

## 1. Error Analysis 的目标

**本分析聚焦于 DIN-style attention 序列模型在真实 session 场景下的失败模式，  
尤其关注：**

- **短 session**
- **稀疏行为**
- **强时序偏置**
- **实时推荐场景下的稳定性问题**

**分析重点不在模型结构本身，而在于 模型在什么条件下失效或收益有限。**

## 2. Error 分类总览

**基于离线评估与人工 case review，主要错误可归为以下四类：**

1. **Short Session Degeneration**
2. **Attention Collapse under Sparse Signals**
3. **Over-weighted Recency Bias**
4. **Latency-Complexity Mismatch**

## 3. Error Type 1：短 Session 下序列模型退化

### 现象

**在 session 长度 ≤ 2 的情况下：**

- **DIN-style attention 的排序结果  
  与非序列 baseline（如 popularity / static embedding）高度相似**
- **排序结果对用户即时意图区分度有限**

### 示例场景

**Session: [click item_A]**

**Query / context: snack-related browsing**

**Top-K 结果：**
- **主要由高点击 / 热门 item 构成**
- **与 session 中唯一行为弱相关**

### 问题定位

- **Attention 机制缺乏足够上下文**
- **Query-Key 匹配退化为全局统计特征**
- **模型行为接近 popularity-based ranking**

### 错误类型

- **Sequence Signal Insufficiency**
- **Model Degeneration on Short Sessions**

### 当前结论

**在极短 session 场景下，序列模型无法显著优于非序列方法。**

---

## 4. Error Type 2：稀疏行为导致 Attention Collapse

### 现象

**在包含大量 view / weak click、但缺乏 purchase 或强反馈的 session 中：**

- **Attention 权重高度集中或近似均匀**
- **无法有效区分关键行为**

### 示例场景

**Session: [view A, view B, view C]**

**Attention 权重分布：**

```
A: 0.33, B: 0.34, C: 0.33
```

### 问题定位

- **隐式反馈信号噪声高**
- **DIN 中 attention score 难以学习有效对比**
- **行为类型区分度不足**

### 错误类型

- **Attention Collapse**
- **Noisy Implicit Feedback**

### 当前结论

**序列模型在弱信号主导的 session 中，attention 难以形成有效偏好表达。**

---

## 5. Error Type 3：Recency 过强导致长期偏好被抑制

### 现象

**当模型对最近行为赋予较高权重时：**

- **最近一次点击主导排序**
- **长期稳定偏好 item 被系统性压制**

### 示例场景

**Session: [frequent healthy food clicks, recent dessert click]**

**排序结果：**
- **Dessert item 被过度提升**
- **Healthy item 排名显著下降**

### 问题定位

- **Recency weighting 与 attention 叠加**
- **对短期噪声行为过度敏感**

### 错误类型

- **Recency Bias**
- **Preference Drift Misinterpretation**

### 当前结论

**在部分场景中，recency 强化会放大噪声而非真实意图。**

---

## 6. Error Type 4：模型复杂度与实时推理不匹配

### 现象

- **序列模型在离线指标上有小幅提升**
- **但推理 latency 明显高于非序列 baseline**
- **在短 session 场景下，性能收益不稳定**

### 问题定位

- **Attention 计算与序列长度线性相关**
- **短 session 下收益不足以抵消推理成本**

### 错误类型

- **Cost-Benefit Mismatch**
- **Inference Inefficiency**

### 当前结论

**在实时推荐系统中，序列模型的使用需严格受场景与 session 条件约束。**
