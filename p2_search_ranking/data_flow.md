# Project 2 -- Search & Ranking System

## Overview

This document describes the **end-to-end data flow** of the ranking system,  
from **raw interaction logs** to **feature construction**, and finally to **model training and inference**.

The goal is to make clear:

- 数据从哪里来
- 经过了哪些处理
- 模型真正"吃"的是什么

## 1. Logging Layer（日志采集）

### 1.1 原始日志来源（模拟真实系统）

系统假设存在如下基础日志（离线构造 / 模拟）：

- **User Interaction Logs**
  - user_id
  - item_id
  - event_type（click / view / purchase）
  - timestamp

- **Item Metadata**
  - item_id
  - category
  - price
  - popularity（历史点击或销量统计）

- **Query / Intent Signals（模拟）**
  - cuisine / preference / popularity 等意图标签
  - 由用户历史行为或规则生成

**说明：**  
由于是个人项目，日志由公开数据集（如 Amazon Reviews）重构而来，用于**近似真实搜索 / 推荐场景**。

## 2. Data Preprocessing（日志 → 样本）

### 2.1 行为日志清洗

- 去除缺失 user_id / item_id 的记录
- 按时间排序，构建 session-like 行为序列
- 过滤极低频用户 / 物品（减少噪声）

### 2.2 样本构造（Training Pairs）

根据行为日志构造训练样本：

- **正样本（Positive）**
  - (query / intent, clicked_item)

- **负样本（Negative）**
  - 同一 query 下未点击的 item
  - 或随机采样的非相关 item

用于支持：
- pointwise / pairwise ranking 训练
- offline evaluation（Recall@K / NDCG@K）

## 3. Feature Engineering（样本 → 特征）

### 3.1 User / Query Side Features

- 用户偏好统计（历史点击类别分布）
- 当前 query / intent embedding
- 近期行为特征（recency）

### 3.2 Item Side Features

- Item embedding（由文本 / metadata 生成）
- 类别、价格区间
- 流行度特征（popularity baseline）

### 3.3 Cross Features（可选）

- Query × Item 匹配特征
- 类别一致性
- 语义相似度（embedding cosine similarity）

## 4. Model Layer（特征 → 预测）

### 4.1 Recall Stage（候选召回）

- 基于 embedding 的 ANN 搜索（FAISS）
- 输入：query embedding
- 输出：Top-N 候选 item（如 N=100 / 200）

**目标：**
- 高 Recall
- 低延迟
- 不追求精排质量

### 4.2 Ranking Stage（精排）

- **输入：**
  - Query features
  - Item features
  - Cross features

- **输出：**
  - relevance / click likelihood score

**模型目标：**
- 将 **更相关的 item 排在更前面**
- 优化 NDCG@K / CTR proxy

## 5. Inference & Serving Flow（线上）

1. 接收用户 query / intent
2. 生成 query embedding
3. FAISS 召回候选 item
4. 构造 ranking 特征
5. 模型打分并排序
6. 返回 Top-K 结果

## 6. Offline vs Online Data Flow（简要）

| **阶段** | **Offline** | **Online** |
|----------|-------------|------------|
| 数据 | 历史日志 | 实时请求 |
| 特征 | 可复杂 | 需轻量 |
| 目标 | 评估模型能力 | 延迟 + 稳定性 |
| 指标 | Recall / NDCG | CTR / latency |

## 7. Design Considerations

- 日志 → 特征 → 模型 **层次清晰，便于调试**
- Recall 与 Rank 解耦，降低系统复杂度
- 特征设计遵循：
  - 可解释
  - 可增删
  - 不绑定单一模型

## 8. Limitations

- 使用重构日志，无法完全复现真实线上噪声
- Query / intent 为模拟生成
- 未引入真实曝光偏差（position bias）

但足以：
- 说明系统设计思路
- 支撑 offline evaluation 与面试讨论

## 一句话的总结版

"这个项目的数据流是：  
从用户交互日志出发，构造 query-item 训练样本，  
经特征工程后分别用于召回和排序模型，  
离线用 NDCG/Recall 评估，线上关注 latency 和稳定性。"
