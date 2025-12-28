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
