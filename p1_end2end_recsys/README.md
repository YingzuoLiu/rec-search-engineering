# Scenario: Search + Recommendation Platform 

X 是一个多业务 super-app：用户在 XFood（餐饮/外卖） 和 XPay（支付/金融服务） 中既会“主动找”（Search），也会“被引导发现”（Recommendation）。平台化的 Search + Rec 能复用统一的 索引、特征、召回、排序、实验评估与在线服务，让不同业务线用同一套基础能力更快迭代：
Search（明确意图）：用户输入 query（如“奶茶”“炸鸡”“附近便利店”），需要高相关、低延迟的结果。
Rec（弱意图/发现）：用户在首页/频道/结算页看到个性化推荐（餐厅、菜品、优惠券、金融产品入口），目标是提升 discovery→conversion。
共同挑战：多语言（英语/中英混合）、地理位置强相关、时效性（营业/库存/配送）、商家/活动快速变化、冷启动（新用户/新店/新活动）。

# Pipeline

[1) Data Sources]
- User behavior: impressions, clicks, orders, add-to-cart, dwell
- Search logs: query, clicked items, reformulations
- Item/merchant data: title/desc, category, price, location, open hours
- Context: user geo, time-of-day, device, campaign/discount
- (Optional) Payments/finance events for XPay surfaces (high-level preference signals) eg.uses_discount_often = True

            |
            v

[2) ETL + Feature Store]
- Clean & join events (dedup, sessionize)
- Build features:
  - User: recent history, preferences, price sensitivity, region
  - Item/Merchant: popularity, freshness, availability, quality
  - Query: normalized tokens, spelling variants, language ID
- Store online-ready features (keyed by user_id / item_id / merchant_id)

            |
            v

[3) Representation / Embeddings]
- Item embedding (text + category + metadata)
- User embedding (recent interacted items / sequence summary)
- Query embedding (for semantic retrieval)
- (Optional) multilingual normalization

            |
            v

[4) Candidate Generation (Recall)]
A. Search Recall (query-driven)
- Lexical: inverted index (BM25/keywords)
- Semantic: ANN over item embeddings (query->item)
- Geo/availability filters (open now, deliverable, within radius)

B. Recommendation Recall (user-driven)
- ANN over item embeddings (user->item)
- Popularity/freshness fallback for cold-start users
- Business constraints (category, budget, region)

            |
            v

[5) Ranking]
- Score candidates with a light model:
  - similarity (user/query, item)
  - structured features (price, distance, ETA, discount, popularity, freshness)
  - context features (time, location)
- Output: top N ranked list

            |
            v

[6) Re-ranking + Constraints]
- Diversity (avoid near-duplicates, category balance)
- Policies/guardrails (availability, sponsored slots, fairness if needed)
- Final top K list returned to UI

            |
            v

[7) Serving + Monitoring]
- Online latency budget (caching, precompute embeddings)
- Metrics:
  - Search: NDCG@K, CTR, reformulation rate
  - Rec: CTR, CVR/order rate, revenue proxy, coverage/diversity
- Experimentation: A/B or offline replay evaluation

