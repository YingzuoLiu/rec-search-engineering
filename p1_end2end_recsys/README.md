# Search + Recommendation Platform (Super-App)

X 是一个多业务 super-app。  
用户在 XFood（餐饮 / 外卖） 和 XPay（支付 / 金融服务） 中，既会：

- 主动找（Search）
- 被引导发现（Recommendation）

平台化的 Search + Recommendation 能力，复用统一的：

- 索引（Index）
- 特征（Features）
- 召回（Recall）
- 排序（Ranking）
- 实验评估（Experimentation）
- 在线服务（Serving）

从而让不同业务线在同一套基础设施上更快迭代。

---

## 1. Use Cases

### Search（明确意图）

- 用户输入 query  
  - 示例：`奶茶`、`炸鸡`、`附近便利店`
- 目标：
  - 高相关性
  - 低延迟
  - 强约束（地理 / 营业 / 配送）

### Recommendation（弱意图 / 发现）

- 出现位置：
  - 首页
  - 频道页
  - 结算页
- 推荐对象：
  - 餐厅
  - 菜品
  - 优惠券
  - 金融产品入口
- 目标：
  - 提升 discovery → conversion

---

## 2. Shared Challenges

- 多语言（英语 / 中英混合）
- 强地理位置相关
- 强时效性
  - 营业状态
  - 库存
  - 配送能力
- 商家 / 活动快速变化
- 冷启动问题
  - 新用户
  - 新店
  - 新活动

---

## 3. End-to-End Pipeline

```
[1) Data Sources]
        |
        v
[2) ETL + Feature Store]
        |
        v
[3) Representation / Embeddings]
        |
        v
[4) Candidate Generation (Recall)]
        |
        v
[5) Ranking]
        |
        v
[6) Re-ranking + Constraints]
        |
        v
[7) Serving + Monitoring]

```
---

## 4. Pipeline Details

### 4.1 Data Sources

- User behavior
  - impressions
  - clicks
  - orders
  - add-to-cart
  - dwell
- Search logs
  - query
  - clicked items
  - reformulations
- Item / Merchant data
  - title / description
  - category
  - price
  - location
  - open hours
- Context
  - user geo
  - time-of-day
  - device
  - campaign / discount
- (Optional) Payments / finance events (XPay)
  - high-level preference signals  
    - e.g. `uses_discount_often = true`

---

### 4.2 ETL + Feature Store

- Clean & join events
  - dedup
  - sessionize
- Build features
  - User
    - recent history
    - preferences
    - price sensitivity
    - region
  - Item / Merchant
    - popularity
    - freshness
    - availability
    - quality
  - Query
    - normalized tokens
    - spelling variants
    - language ID
- Store online-ready features
  - keyed by `user_id / item_id / merchant_id`

---

### 4.3 Representation / Embeddings

- Item embedding
  - text + category + metadata
- User embedding
  - recent interacted items
  - sequence summary
- Query embedding
  - semantic retrieval
- (Optional) multilingual normalization

---

### 4.4 Candidate Generation (Recall)

#### A. Search Recall (Query-Driven)

- Lexical
  - inverted index
  - BM25 / keywords
- Semantic
  - ANN over item embeddings
  - query → item
- Filters
  - open now
  - deliverable
  - within radius

#### B. Recommendation Recall (User-Driven)

- ANN over item embeddings
  - user → item
- Cold-start fallback
  - popularity
  - freshness
- Business constraints
  - category
  - budget
  - region

---

### 4.5 Ranking

- Light ranking model
- Feature groups
  - similarity (user / query ↔ item)
  - structured features
    - price
    - distance
    - ETA
    - discount
    - popularity
    - freshness
  - context features
    - time
    - location
- Output
  - top N ranked list

---

### 4.6 Re-ranking + Constraints

- Diversity
  - avoid near-duplicates
  - category balance
- Policies / guardrails
  - availability
  - sponsored slots
  - fairness (if needed)
- Output
  - final top K list returned to UI

---

### 4.7 Serving + Monitoring

- Online serving
  - latency budget
  - caching
  - precompute embeddings
- Metrics
  - Search
    - NDCG@K
    - CTR
    - reformulation rate
  - Recommendation
    - CTR
    - CVR / order rate
    - revenue proxy
    - coverage / diversity
- Experimentation
  - A/B testing
  - offline replay evaluation

---

### 5.0 Limitations & Future Work

**Limitations**
- 本项目主要基于离线构造的查询与交互数据进行评估，无法完全覆盖真实线上用户行为中的噪声与偏差。
- 当前排序模型为轻量级设计，未显式建模跨 session 的长期偏好或用户生命周期变化。
- 延迟评估基于小规模请求模拟，未充分验证在高 QPS 场景下的稳定性与资源占用情况。

**Future Work**
- 若应用于生产环境，可结合线上 A/B 测试或反事实评估方法（如 IPS）验证离线指标提升的真实业务效果。
- 在可控延迟预算下，引入更丰富的用户上下文或序列特征，权衡模型复杂度与实时性。
- 增加缓存、请求合并（batching）与降级策略，以提升高并发场景下的服务稳定性。
