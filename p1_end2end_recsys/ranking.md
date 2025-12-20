# Ranking 在推荐/搜索系统中的完整指南

## 1. Ranking 在推荐/搜索系统中的角色

Ranking 的目标不是"找对东西"，而是：

**在给定候选集合的前提下，把"最合适的内容"排在最前面**

在工业级系统中，Ranking 通常发生在：
- Recall 之后（候选量 100-1000）
- Serving 之前（最终展示 Top-K）

## 2. Ranking 的目标函数（Objective Function）

### 2.1 抽象目标

从建模角度，Ranking 的目标可以统一写成：

$$\underset{\theta}{\max}\text{\:\,}\mathbb{E}_{(u,i)}\lbrack\sum_{k}^{}{}w_{k} \cdot f_{k}(u,i)\rbrack$$

其中：
- $u$：用户
- $i$：物品/内容/意图
- $f_{k}$：不同目标（点击、转化、停留、满意度等）
- $w_{k}$：业务权重
- $\theta$：模型参数

👉 **这说明 Ranking 天然是一个「多目标优化问题」**

### 2.2 常见 Ranking 目标

#### （1）Relevance-oriented（相关性导向）

- **目标**：内容是否"匹配用户意图"
- **常用信号**：
  - 点击（CTR）
  - Query-Item / Intent-Action 相似度
- **常见损失**：
  - Cross-Entropy
  - Pairwise loss（如 BPR）

**适合场景**：
- 搜索
- 客服意图推荐
- 信息检索

#### （2）Engagement-oriented（参与度导向）

- **目标**：用户是否"愿意持续互动"
- **常用信号**：
  - 停留时长
  - 连续点击
  - 转化率（CVR）
- **常见建模方式**：
  - 多任务学习（CTR + CVR）
  - 序列建模（DIN / DIEN）

**适合场景**：
- Feed 流
- 内容推荐
- 电商首页

#### （3）Business-oriented（业务导向）

- **目标**：平台收益或成本约束
- **常见信号**：
  - GMV
  - 客服转人工成本
  - SLA / 延迟
- **常见做法**：
  - 加权目标
  - 约束优化（Lagrangian）
  - RL / Bandit

⚠️ **面试要点（一定要会说）**

Ranking 的目标函数**不是固定的**，而是业务目标在模型层的映射。

## 3. Relevance vs Engagement（核心对比）

### 3.1 定义对比

| **维度** | **Relevance** | **Engagement** |
|----------|---------------|----------------|
| 核心问题 | "对不对" | "值不值得继续看" |
| 时间尺度 | 短期 | 中长期 |
| 常见指标 | CTR, NDCG | Dwell Time, CVR |
| 典型模型 | Dual Encoder, BM25, Cross-Encoder | DIN, DIEN, PLE |
| 风险 | 过于保守 | Clickbait / 过拟合 |

### 3.2 为什么二者会冲突？

- **高 Relevance ≠ 高 Engagement**
  - 用户可能点了，但马上离开
- **高 Engagement ≠ 真相关**
  - 标题党、误导性内容

👉 所以工业系统中几乎**不会只优化一个目标**

### 3.3 工业界的解决方式

#### （1）多任务学习（最常见）

同时预测：
- CTR（是否点）
- CVR / Dwell（是否满意）

例如：
- DeepFM + MMoE / PLE
- Shared-bottom + task heads

#### （2）阶段化目标

- Recall / 粗排：偏 Relevance
- 精排 / 重排：引入 Engagement 和 Business

👉 **不是一个模型解决所有问题**

#### （3）加权融合（简单但常用）

$$score = \alpha \cdot relevance + \beta \cdot engagement$$

权重由：
- A/B 实验
- 不同市场/场景决定

⚠️ **面试要点（非常重要）**

Relevance 是"必要条件"，Engagement 是"优化目标"，不是二选一。

## 4. Ranking 的评估指标（补充）

- **离线**：
  - NDCG@K
  - AUC / CTR-AUC
- **在线**：
  - CTR
  - CVR
  - Session-level metrics
- **业务**：
  - GMV
  - 成本/转人工率

👉 **最终以 Online A/B 为准**

## 6. Ranking 的 Loss 设计（How）

### 6.1 为什么 Ranking ≠ 普通分类问题？

虽然 Ranking 常常用点击/转化作为监督信号，但本质上：

**Ranking 关心的是"相对顺序"，而不是"绝对判断"**

因此直接把 Ranking 当二分类，会带来两个问题：
- 忽略候选之间的相对位置
- Offline accuracy 高，但排序效果差

### 6.2 三类常见 Ranking Loss

#### （1）Pointwise Loss（最简单）

**形式**
- 把每个 (user, item) 当成一个样本
- 预测点击概率

常见：
- Binary Cross Entropy（CTR 预估）
- MSE（回归型 engagement）

**优点**
- 实现简单
- 易收敛
- 工业中非常常见（尤其粗排）

**缺点**
- **不直接优化排序**
- 对 Top-K 顺序不敏感

⚠️ 面试要点：

Pointwise loss 更像是在做"相关性打分"，而不是"排序对比"。

#### （2）Pairwise Loss（最常用）

**核心思想**

**正样本的 score 应该高于负样本**

典型 loss：
- BPR Loss
- Hinge Loss
- Pairwise Logistic Loss

形式示意：

$$\mathcal{L = -}\log\sigma(s^{+} - s^{-})$$

**优点**
- 直接建模相对顺序
- 对排序更友好

**缺点**
- 负样本构造敏感
- batch 设计复杂

⚠️ 面试要点：

Pairwise loss 是工业 ranking 的主流选择之一，尤其在精排阶段。

#### （3）Listwise Loss（理论最优，工程最难）

**核心思想**
- 直接优化整个列表
- 对齐 NDCG / MAP 等指标

代表：
- ListNet
- LambdaRank / LambdaMART

**优点**
- 与最终排序指标最一致

**缺点**
- 实现复杂
- 计算开销大
- 工业中多用于 tree-based ranking

⚠️ 面试要点：

深度模型中较少纯 listwise，更多是 pairwise + 近似 listwise。

## 7. Relevance vs Engagement 的 Label 构建

### 7.1 Relevance 的 Label（相对清晰）

常见来源：
- Click / No-click
- Query-Item relevance 标注
- Intent-Action 是否匹配

特点：
- 二值
- 噪声相对较小
- 适合 CE / Pairwise

### 7.2 Engagement 的 Label（工业难点）

常见 engagement 信号：
- 停留时长（Dwell Time）
- 是否完成任务
- 转化/连续行为

**问题 1：是连续值，怎么训练？**

常见做法：
1. **分桶（Bucketize）**
   - short / medium / long
2. **阈值化**
   - T 秒 = 正样本
3. **回归**
   - 直接预测 dwell time（较少）

**问题 2：噪声很大，怎么办？**
- Sample reweighting
- Log transform（缓解长尾）
- 与 CTR 做多任务约束

⚠️ 面试要点（非常重要）：

Engagement 通常不会单独训练，而是作为多任务的一部分，与 relevance 互相约束。

## 8. 多目标 Ranking 的实现方式

### 8.1 多任务学习（主流方案）

结构：
- Shared Bottom
- Task-specific heads（CTR / CVR / Dwell）

模型示例：
- MMoE
- PLE

好处：
- 自动平衡 relevance 与 engagement
- 提升泛化能力

### 8.2 加权融合（简单有效）

$$score = \alpha \cdot relevance + \beta \cdot engagement$$

权重来源：
- A/B 实验
- 市场/场景配置

⚠️ 面试要点：

权重不是拍脑袋定的，而是通过线上实验调优。

## 9. Ranking 的评估闭环（Offline → Online）

### 9.1 离线评估

常见指标：
- AUC / CTR-AUC
- NDCG@K
- Recall@K

⚠️ 限制：
- 离线提升 ≠ 线上提升

### 9.2 在线评估（最终标准）

- CTR
- CVR
- Dwell Time
- Session-level metrics
- Business metrics（GMV / 成本）

👉 **所有 Ranking 改动最终必须通过 A/B 实验验证**

### 9.3 为什么 Offline 好但 Online 不涨？

常见原因：
- Label bias（曝光偏差）
- Distribution shift
- 目标函数与业务目标不一致

这也是：
- Bandit
- IPS / DR
- RL

出现的原因（后续章节展开）。

## 10. 总结

- Ranking 是一个多目标优化问题
- Relevance 保证"对"，Engagement 保证"值不值得"
- Loss 决定模型在"学什么顺序"
- Engagement label 是工业难点
- 最终效果以 Online A/B 为准

---

## 面试问答实战

### Q1: Ranking 的核心目标

**面试官问**：你刚才提到 Ranking 是一个多目标优化问题。那在 XFood / XPay 这种场景里，Ranking 的核心目标到底是什么？

**⭐ 面试合格回答（参考）**

在 X 的场景下，Ranking 通常不是单一目标，而是一个多目标问题。基础目标是 relevance，确保推荐内容和用户当前意图匹配；在此基础上，引入 engagement 指标，比如点击后是否继续浏览、是否完成交易或操作；同时还会受到业务约束，比如 GMV、补贴成本或客服转人工成本。实际上这些目标不会完全合并到一个 loss 里，而是通过多任务或分阶段的方式实现。

#### 工业里通常怎么"拆"这个多目标？

**方式 A：同一条 pipeline，但多个 stage（最常见）**

Recall → Light rank (CTR/relevance) → Heavy rank (multi-task) → Re-rank (business constraints)

- **粗排**：算得快，先保 relevance/CTR，砍掉一大堆
- **精排**：算得准，多任务（CTR + CVR/engagement）
- **重排**：加业务约束（GMV、补贴成本、探索、新商家等）

直觉：越靠后，越贵、越贴近业务规则。

**方式 B：同一个 ranker，多头输出（multi-head / multi-task）**

```
shared encoder
├─ head_ctr
├─ head_cvr
└─ head_dwell/engagement

final_score = w1*ctr + w2*cvr + w3*engagement (+ constraints)
```

- 训练时是 **多个 loss**
- 线上 serving 时是 **一个 score**（但由多个 head 融合）

这不是多条 pipeline，而是一个 ranker 的"多输出"。

**方式 C：多条"召回路径 / cohort 路径"（新商家就是这个）**

```
recall_popular
recall_personalized
recall_new_merchant
recall_ann_embedding
→ merge / dedup / quota
→ rank
```

- 这是"多条路"，但它主要发生在 **Recall** 层
- 然后在 Rank / Re-rank 做统一融合和约束

#### "道路不同"具体长啥样

下面是一个 **toy** 的代码骨架："多条路"但最终会汇成一个排序。

**(1) 多路召回 + 合并**

```python
def retrieve_candidates(user, ctx):
    cands = []
    cands += recall_personalized(user, ctx, k=200)
    cands += recall_popular_nearby(user, ctx, k=200)
    cands += recall_ann_embedding(user, ctx, k=200)  # 可选
    cands += recall_new_merchants(user, ctx, k=80)  # cohort 路径
    
    cands = dedup_and_cap(cands, cap=600)  # 去重 + 总量控制
    return cands
```

**(2) 粗排：快、偏 relevance/CTR**

```python
def light_rank(user, ctx, cands):
    feats = build_features(user, ctx, cands, light=True)
    ctr = ctr_model.predict(feats)  # pointwise CE 训练出来的
    top = topk_by_score(cands, ctr, k=200)
    return top
```

**(3) 精排：多任务输出（CTR/CVR/engagement）**

```python
def heavy_rank(user, ctx, cands):
    feats = build_features(user, ctx, cands, light=False)
    pred = multitask_model.predict(feats)  # {"ctr":..., "cvr":..., "dwell":...}
    return pred
```

**(4) 业务重排：GMV/补贴/成本/探索约束**

```python
def rerank_with_constraints(user, ctx, cands, pred):
    # 一个常见做法：先算 base_score，再做约束重排
    base = (0.6 * pred["ctr"] + 0.3 * pred["cvr"] + 0.1 * pred["dwell"])
    
    # 例：成本约束（补贴/转人工成本）以 penalty 形式进入
    penalty = estimate_cost(user, ctx, cands)  # 越高越差
    score = base - 0.05 * penalty
    
    # 例：新商家探索配额（quota），不直接"强行加权"到 rank loss
    scored = list(zip(cands, score))
    final = quota_rerank(scored, quota={"new_merchant": 0.1})  # TopK 里留 10% 新商家
    
    return final[:50]
```

你看：
- relevance/engagement 多目标主要体现在 **heavy rank 的多头预测**
- GMV/成本等业务约束更常在 **rerank 做受控融合**
- 新商家更常用 **召回路径 + rerank quota/探索**，而不是在 ranking 里硬塞

#### "不会完全合并到一个 loss"到底怎么实现？

你可以把它理解成两层：

**训练层（Training）**
- 多任务模型：
  ```
  loss = w_ctr*L_ctr + w_cvr*L_cvr + w_dwell*L_dwell
  ```
- 业务约束（GMV/成本）很多时候**不直接作为监督 loss**（因为 label 不干净、延迟长、归因难）

**线上层（Serving）**
- 输出多个预测值
- 通过可配置权重/规则融合
- 用 A/B 调权重、调 quota、调 penalty

这就是为什么面试我会一直强调：

**目标函数 ≠ 单一 loss，而是"训练目标 + serving 融合 + 策略约束"的组合。**

**追问 1：Relevance 和 Engagement 哪个更重要？**

**回答**

Relevance 是必要条件，engagement 是优化目标。如果内容本身不相关，高 engagement 往往是噪声或误导；但如果只优化 relevance，会导致用户点了就走。所以工业系统中通常先保证 relevance，再在精排或重排阶段优化 engagement。

### Q2: Loss 函数选择

**面试官**：那你在 Ranking 中一般用什么 loss？为什么？

**我在考什么**
- 你是不是只会说 Cross Entropy
- 你是否理解 **排序 ≠ 分类**

**⭐ 标准回答**

这取决于阶段和目标。在粗排阶段，常用 pointwise 的 cross entropy 来做 CTR 预估，稳定且高效；在精排阶段，更倾向于 pairwise loss，比如 BPR 或 hinge loss，因为它直接优化样本之间的相对顺序，更符合 Ranking 的目标。Listwise 理论上最好，但实现和计算成本较高，更多见于 LambdaMART 等 tree-based 模型。

**🔥 追问 2（高频杀手追问）**

**面试官**：那如果你用 pointwise loss，为什么还能做 Ranking？

**⭐ 高分回答**

Pointwise loss 本身不直接建模顺序，但如果样本分布合理、候选集合稳定，它学习到的是一个相关性打分函数。实际排序由 score 决定，所以在工程上 pointwise loss 是一种效率和效果的折中，尤其在粗排阶段。

### Q3: Engagement Label

**面试官**：Engagement 通常用什么 label？比如停留时长，你是怎么训练的？

**❌ 常见翻车回答**
- "直接回归 dwell time"
- "用平均时长"

**⭐ 合格回答**

Engagement 的 label 通常噪声较大，比如停留时长是连续值且长尾明显。实际中常见做法是分桶或阈值化，比如将 dwell time 转为短/中/长，或者超过某个阈值视为正样本。同时 engagement 往往不会单独训练，而是作为多任务的一部分，与 CTR 等 relevance 目标一起约束模型。

**🔥 追问 3**

**面试官**：如果 relevance 和 engagement 冲突了，你怎么办？

**⭐回答**

通常不会在一个阶段强行解决冲突。在召回和粗排阶段更偏向 relevance，保证意图正确；在精排或重排阶段再引入 engagement，通过多任务权重或 rerank 策略平衡。权重不是固定的，而是通过 A/B 实验在不同市场或场景下调优。

### Q4: Offline vs Online

**面试官**：你刚才说最终以 A/B 为准，那为什么经常出现 offline 指标涨了，online 没涨？

**⭐ 高分回答**

常见原因包括曝光偏差、分布漂移，以及 offline 目标函数与真实业务目标不一致。Offline 数据通常来自历史曝光，模型可能过拟合已有排序；而线上用户行为会因为推荐变化而发生反馈环。所以 ranking 的最终验证一定要通过在线 A/B 实验。

### Q5: 为什么不直接用 RL

**面试官**：那既然 offline 有偏差，为什么不一开始就用 RL？

**⭐ 高级回答**

RL 在 ranking 中确实可以建模长期收益，但它对 reward 设计、探索成本和稳定性要求很高。在工业实践中，通常先用 supervised ranking 建立一个强基线，再在重排或策略层引入 bandit 或 RL，用于解决探索和长期优化问题。

---

## 高频追问题库

### Q1｜Ranking 和 Recall 的边界是什么？

**✅ 推荐回答（你可以直接用）**

Recall 的目标是**覆盖**，尽量把"可能相关"的候选找出来；Ranking 的目标是在候选集合已经合理的前提下，**做精细化排序**。所以 Recall 更关注召回率和多样性，而 Ranking 更关注相关性、用户体验和业务目标。不适合在 Ranking 里解决"根本没被召回"的问题，否则会让排序模型背负不该承担的责任。

**🔥 追问 A1｜新商家在 Ranking 里永远排不上来怎么办？**

**✅ 推荐回答**

这种情况我不会直接在 Ranking 里强行加权。更合理的做法是在 Recall 层为新商家设计单独的召回路径，或者在重排阶段加入探索策略。Ranking 本身应该保持对 relevance 和 engagement 的建模一致性，否则会影响整体排序稳定性和指标解释。

### Q2｜多目标 Ranking 是怎么体现在 loss 里的？

**✅ 推荐回答**

多目标通常不会简单地合成一个 loss。实际中更常见的是多任务学习，比如一个 shared backbone，同时预测 CTR、转化或 engagement 等不同目标。每个任务有自己的 loss，通过任务权重或结构设计来平衡不同目标。

**🔥 追问 B1｜Relevance 和 Engagement 是放在一个 loss 里，还是分开？**

**✅ 推荐回答**

通常是分开建模、共享表示。Relevance 和 engagement 的信号分布和噪声特性不同，强行合成一个 loss 容易互相干扰。通过多任务结构既能共享用户和内容表示，又能让不同目标有各自的优化空间。

### Q3｜只优化 relevance 或 engagement，会发生什么？

**✅ 推荐回答**

如果只优化 relevance，推荐内容在语义上是对的，但用户可能点了就走，体验不佳；如果只优化 engagement，容易出现标题党或误导内容，短期指标好但长期信任下降。所以工业系统通常把 relevance 作为必要条件，在此基础上再优化 engagement。

**🔥 追问 C1｜在 XFood 场景里，你更偏哪一个？**

**✅ 推荐回答（一定要"选边"）**

在 XFood 场景下我会更偏向 relevance 作为底线。用户通常有明确即时意图，如果推荐不相关，哪怕 engagement 高也很容易流失。在保证 relevance 的前提下，再通过精排或重排阶段优化 engagement，比如停留或转化。

### Q4｜Offline 指标涨了，Online A/B 没涨，怎么排查？

**✅ 推荐回答**

我会先确认 offline 和 online 的目标是否一致，其次检查是否存在曝光偏差或分布漂移。很多 offline 数据来自历史排序，模型可能只是拟合了已有曝光，而没有真正改善排序。如果模型逻辑合理，最终还是要以在线 A/B 的结果作为判断依据。

**🔥 追问 D1｜如果模型本身没问题，你还会看什么？**

**✅ 推荐回答**

我会进一步检查实验配置，比如流量是否干净、是否存在策略干扰。同时也会看用户行为是否发生变化，比如模型调整后用户点击模式是否改变。有时候问题不在模型，而在策略、曝光或实验设计本身。

### Q5｜Ranking 目标是 Top-K，为什么还用 AUC？

**✅ 推荐回答**

AUC 衡量的是模型整体区分正负样本的能力，稳定且易比较。虽然它不直接对齐 Top-K 排序，但在候选集分布相对稳定时，AUC 可以作为有效的 proxy。实际中通常结合 AUC 和 NDCG 等指标一起评估。

**🔥 追问 E1｜什么时候 AUC 会误导你？**

**✅ 推荐回答**

当模型在尾部样本上提升较多，但对 Top-K 排序影响不大时，AUC 可能上涨但用户体验没有改善。或者当候选分布发生变化时，AUC 的对比意义会下降。所以最终还是需要结合 Top-K 指标和线上实验判断。

---

## ✅ 必须掌握的 5 个场景（Day 3 对应）

### ① 多阶段 ranking pipeline

- Recall → Rank → Re-rank
- 为什么要拆
- 每一层负责什么

**面试：必问**

### ② pointwise vs pairwise 的使用场景

- 为什么粗排用 CE
- 为什么精排用 pairwise
- trade-off 是什么

**面试：高频**

### ③ 多目标 score 融合

- ctr / cvr / engagement
- 加权
- 多任务 vs rerank

**面试：必考**

### ④ Offline 指标 vs Online A/B

- AUC 为什么会骗人
- NDCG@K 什么时候更好
- 分布变化怎么影响指标

**面试：非常爱追问**

### ⑤ 不该在 ranking 里做的事

- 新商家硬加权
- GMV 直接塞进 loss
- 所有问题都往 rank 里推

**面试："踩雷题"**