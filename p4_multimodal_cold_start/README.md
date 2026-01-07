# Multimodal Item Representation for Cold-Start Recommendation

**Tech Stack:** PyTorch · CLIP · FAISS  
**Dataset:** Amazon Product Images + Titles + Metadata

---

## 📌 Project Motivation

In real-world search and recommendation systems, **cold-start items** (new products, new merchants, newly listed content) often suffer from poor exposure due to the lack of user interaction history.

This project focuses on **item-side cold start**, exploring how **multimodal signals (image + text)** can be leveraged to build robust item representations before any behavioral data is available.

---

## 🧠 Where Multimodal Models Fit in the Search Pipeline

This project targets the **Recall / Candidate Generation** stage of a search or recommendation system.

```
User Query
   ↓
Query Understanding
   ↓
🔹 Multimodal Recall (This Project)
   ↓
Lightweight Ranking
   ↓
Serving
```

### Why here?

- Cold-start items cannot rely on collaborative signals.
- Multimodal embeddings allow **semantic recall** even with zero interactions.
- FAISS enables **low-latency ANN retrieval** at scale.

This project intentionally **does not place LLMs in ranking or generation**, keeping inference cost and latency under control.

---

## 🧩 Approach Overview

### 1. Multimodal Item Encoding

Each item is represented using:

- **Image:** Product image
- **Text:** Title + structured metadata

We use **CLIP** to encode both modalities into a **shared embedding space**, enabling semantic alignment between visual and textual information.

```
Image ─┐
       ├─ CLIP Encoder ─→ Item Embedding
Text  ─┘
```

### 2. Vector Indexing with FAISS

- Item embeddings are indexed using **FAISS ANN search**
- Enables fast similarity-based retrieval for:
  - text queries
  - image queries
  - hybrid search scenarios

This setup simulates **production-style recall infrastructure**.

---

## 🔍 Evaluation Strategy

Since cold-start items lack interaction data, evaluation focuses on **retrieval robustness** rather than CTR.

### Baselines

- Text-only embedding
- Multimodal (Image + Text) embedding

### Metrics

- Recall@K on held-out cold-start items
- Qualitative retrieval inspection

### Findings

- Multimodal embeddings show **more stable recall** for visually distinctive items.
- Text-only models degrade when titles are short or ambiguous.
- Image signals provide **complementary semantic cues**.

---

## 🧪 Ablation Study

To better understand modality contribution, we conduct a small-scale ablation:

| Setting | Observation |
|---------|-------------|
| Image only | Strong for appearance-driven items |
| Text only | Sensitive to sparse or noisy titles |
| Image + Text | Most robust overall |

This confirms that **multimodal fusion improves cold-start recall consistency**, rather than maximizing a single metric.

---

## 🍔 Applicability to Food & Merchant Discovery

This approach naturally extends to:

- Food discovery (dish photos + descriptions)
- Merchant onboarding (store images + profiles)
- Local discovery platforms

In such scenarios:

- Visual cues are often as important as text
- Cold-start is frequent and unavoidable

---

## ⚖️ Design Trade-offs

### Pros

- No dependency on user behavior
- Strong cold-start performance
- Scales well with FAISS

### Cons

- Multimodal encoders increase offline compute cost
- Requires careful feature hygiene (image quality, text noise)

---

## 🚀 Future Extensions

- Late fusion with behavior-based embeddings once data becomes available
- Query-side multimodal understanding
- Lightweight re-ranking on top of multimodal recall

---

## ✅ Key Takeaway

This project demonstrates how **multimodal representation learning** can be cleanly integrated into the **recall layer** of a search/recommendation system to mitigate cold-start issues—**without introducing heavy LLM dependencies or latency risks**.

## Limitations & Future Work

**Limitations**
- 本项目主要验证多模态信息在冷启动召回场景下的有效性，当前融合方式基于 CLIP 提供的统一 embedding 空间，未对不同模态的重要性进行样本级建模。
- 对于图片缺失或质量较低的商品，多模态表示的稳定性仍依赖文本与基础元数据路径作为隐式 fallback。
- 实验规模相对有限，结果更侧重方法可行性验证，而非给出具有统计显著性的工业级结论。

**Future Work**
- 在保持召回阶段低延迟的前提下，引入 gating 或条件融合机制，使模型能够根据商品特征自适应调整不同模态的贡献。
- 在更贴近真实业务分布的数据上，评估多模态召回对冷启动商品曝光与点击行为的长期影响。
- 设计显式的模态降级与路由策略，提高系统在模态缺失或噪声场景下的鲁棒性。
