# Project 2 — Search Ranking with User Behavior Modeling
## (Interview-oriented Learning Notes)

## Overview

This project documents my understanding of search ranking systems with user behavior modeling, following an interview-driven learning approach.

The focus is on how short-session user behavior sequences and query understanding are integrated into a practical search ranking pipeline, reflecting real-world constraints such as sparse interactions, recency sensitivity, and latency requirements.

Rather than presenting a single polished model, this project emphasizes system-level thinking, including data flow, evaluation metrics, error analysis, and on-the-spot coding patterns commonly encountered in algorithm interviews.

## Problem Context

In on-demand and search-driven platforms, user behavior is often:

- **Sparse** (few interactions per session)
- **Short-lived** (intent changes quickly)
- **Highly query-dependent**

Traditional non-sequential or long-term preference models may struggle to capture such dynamics. This project explores how session-based user behavior modeling can improve relevance estimation in search ranking scenarios.

## Data Flow Overview

1. Raw interaction logs
   - user_id, item_id, timestamp
   - implicit feedback (view / click / purchase)

2. Session construction
   - group interactions by user
   - split into short sessions based on time gaps

3. Feature preparation
   - query features
   - item features
   - behavior sequence features

4. Model input
   - query as attention target
   - recent behavior sequence as context

## Search Pipeline Position

The project is scoped around the ranking stage of a typical search system:
```
Query
→ Query Understanding
→ Candidate Retrieval
→ Feature & Behavior Modeling
→ Ranking
→ Serving
```

This module focuses on the interaction between query signals and recent user behavior, producing a query-aware representation of short-term user intent for ranking.

## Query Understanding (Search Perspective)

In search systems, the query represents the user's explicit intent at the current moment.

Instead of treating the query as static text, it is used as a conditioning signal for downstream ranking models. In this project, the query guides attention over recent user interactions, enabling query-aware behavior modeling rather than relying solely on historical preferences.

## User Behavior Sequence Modeling

User behavior sequences are constructed from timestamp-ordered implicit feedback signals such as:

- views
- clicks
- purchases

Interactions are grouped into short sessions to better reflect real search usage patterns. Sequence-aware modeling is applied to dynamically emphasize behaviors most relevant to the current query.

DIN-style attention is used conceptually to avoid compressing all past behavior into a fixed embedding, allowing the model to selectively focus on query-relevant interactions.

## Why Short Sessions Matter

Search-driven user sessions are typically short and intent-focused.

Under such conditions:

- Recency often outweighs long-term preference
- Noisy or outdated behaviors can harm relevance
- Sequence-aware models tend to produce more stable ranking signals than non-sequential baselines

This project explicitly analyzes the impact of session length, recency weighting, and behavior sparsity on ranking quality.

## Practical Considerations

While attention-based behavior models can improve relevance modeling, they introduce additional inference cost.

This project discusses the trade-offs between:

- model expressiveness
- inference latency
- engineering complexity

with an emphasis on real-time search ranking constraints.

---

# 项目 2 — 基于用户行为建模的搜索排序
## (面向面试的学习笔记)

## 概述

本项目记录了我对结合用户行为建模的搜索排序系统的理解，采用面向面试驱动的学习方法。

重点是如何将短会话用户行为序列和查询理解集成到实际的搜索排序流水线中，反映现实世界的约束条件，如稀疏交互、时效性敏感性和延迟要求。

本项目不是呈现单一的完善模型，而是强调系统级思维,包括数据流、评估指标、错误分析以及算法面试中常见的现场编码模式。

## 问题背景

在按需服务和搜索驱动的平台中，用户行为通常具有以下特征:

- **稀疏** (每个会话交互很少)
- **短暂** (意图变化快速)
- **高度依赖查询**

传统的非序列化或长期偏好模型可能难以捕捉这种动态特性。本项目探索基于会话的用户行为建模如何改进搜索排序场景中的相关性估计。

## 搜索流水线位置

本项目范围围绕典型搜索系统的排序阶段:
```
查询
→ 查询理解
→ 候选召回
→ 特征与行为建模
→ 排序
→ 服务
```

本模块专注于查询信号与近期用户行为之间的交互，为排序生成查询感知的短期用户意图表示。

## 查询理解(搜索视角)

在搜索系统中，查询代表用户当前时刻的显式意图。

本项目不是将查询视为静态文本，而是将其用作下游排序模型的条件信号。在本项目中，查询引导对近期用户交互的注意力，实现查询感知的行为建模，而不是仅依赖历史偏好。

## 用户行为序列建模

用户行为序列由时间戳排序的隐式反馈信号构建，例如:

- 浏览
- 点击
- 购买

交互被分组为短会话，以更好地反映真实搜索使用模式。应用序列感知建模来动态强调与当前查询最相关的行为。

概念上使用 DIN 风格的注意力机制，避免将所有过去行为压缩为固定嵌入，允许模型选择性地关注与查询相关的交互。

## 为什么短会话很重要

搜索驱动的用户会话通常很短且意图集中。

在这种条件下:

- 时效性通常胜过长期偏好
- 噪声或过时的行为可能损害相关性
- 序列感知模型往往比非序列基线产生更稳定的排序信号

本项目明确分析了会话长度、时效性加权和行为稀疏性对排序质量的影响。

## 实际考虑因素

虽然基于注意力的行为模型可以改进相关性建模，但它们会引入额外的推理成本。

本项目讨论了以下方面的权衡:

- 模型表达能力
- 推理延迟
- 工程复杂性

重点关注实时搜索排序的约束条件。
