# Online Serving Design

## Latency Budget

The online serving pipeline is designed with a strict latency budget
to ensure stable user experience under high QPS.

The total latency budget is approximately 100–120 ms, distributed as:

- Feature fetching & request parsing
- Candidate recall (ANN-based retrieval)
- Ranking model inference
- Lightweight re-ranking logic
- Response serialization

Each stage has a soft timeout. If a stage exceeds its allocated budget,
fallback mechanisms are triggered to guarantee response delivery.

## Caching Strategy

To reduce latency and improve system stability, multiple caching layers
are applied:

- User and item features are cached in memory or Redis with TTL.
- Item embeddings are precomputed offline and cached for online use.
- Popular query results can be cached to optimize head traffic.

Caching introduces a trade-off between freshness and performance,
which is controlled via TTL and cache invalidation policies.

## Fallback Mechanism

The system is designed to degrade gracefully under abnormal conditions.

- If ranking model inference times out, a simplified scoring logic is used.
- If recall services are unavailable, a precomputed popular-item list
  is returned as a fallback.
- The priority is availability over optimal ranking quality.

This design ensures the system remains responsive even under partial
failures or traffic spikes.

## Alerting Strategy

Alerts are configured on critical signals:

- P95 latency exceeding predefined thresholds.
- Error or timeout rate spikes indicating service instability.
- Abnormal increases in fallback rate, suggesting upstream failures.

Alerts are designed to balance sensitivity and noise,
preventing excessive false positives.

---
## Mock Interview
---
## Q：ranking 模型推理超时怎么办?

**回答:**

在 serving 层我会给 ranking inference 设一个 soft timeout。一旦超过这个时间,不会等模型返回,而是直接走 fallback,比如用更轻量的打分逻辑或者热门结果,保证请求能按时返回。

---

## Q:哪些地方用了 cache?为什么?

**回答:**

主要 cache 用户特征、物品特征和预计算的 embedding,因为这些数据访问频繁、变化不算特别快,如果每次请求都实时算或查存储,latency 会不可控。

**加一句更稳的(可选):**

排序模型本身不 cache,但它用到的输入尽量 cache。

---

## Q:cache 会有问题吗?你怎么接受这个 trade-off?

**回答:**

会有,比如数据不是完全最新。但在线上 serving 场景里,性能和稳定性优先于绝对实时一致性,所以通过 TTL 控制这个 trade-off 是可以接受的。

---

## Q:fallback 是不是等于失败?

**回答:**

不是。fallback 是一种正常的降级策略。线上系统里 availability 比最优推荐结果更重要,宁可推荐质量下降,也不能超时或返回空结果。

---

## Q:上线后你会重点看哪些监控指标?

**回答:**

我会同时看两类指标:
- 一类是系统指标,比如 P95 latency、timeout rate
- 另一类是推荐效果指标,比如 CTR 和 fallback rate

---

## Q:latency 正常,但 CTR 连续下降,你怎么想?

**回答:**

说明系统没挂,但推荐质量可能出了问题。可能原因包括模型效果退化、特征分布变化,或者 fallback 比例变高,用户实际看到的是降级结果。

---

## Q:fallback rate 会设 alert 吗?

**标准回答:**

会的。fallback 本身不是异常,但 fallback rate 突然升高往往说明 upstream latency 或模型推理出了问题,即使系统没直接报错,也值得排查。

---

## Q:只能留一个监控指标,你选哪个?

**稳妥版回答:**

我会选 P95 latency。因为它直接决定用户体验和系统是否可用,也是最容易触发一系列 fallback 和连锁问题的指标。
