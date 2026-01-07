# Project 5: Offline Evaluation & Experimentation for Ranking Optimization

## Overview

This project focuses on **offline evaluation and controlled experimentation** for ranking systems, with the goal of understanding **when and why** a ranking strategy improves — rather than chasing single-run metric gains.

Using simulated interaction logs derived from Amazon Reviews, I built a lightweight but systematic evaluation framework to compare retrieval and ranking strategies under different experimental settings.

The project emphasizes:

- metric-driven iteration
- reproducibility
- awareness of offline vs online gaps

rather than claiming production-level performance.

## Dataset

### Source
Amazon Reviews (public dataset)

### Processing
- Converted user–item interactions into simplified implicit feedback logs
- Simulated ranking candidates and relevance labels for offline evaluation

### Purpose
- Enable controlled, repeatable experiments without relying on online traffic

This setup mirrors early-stage ranking research or pre-A/B experimentation commonly done before online deployment.

## Offline Evaluation Framework

I implemented an offline evaluation pipeline to compare different ranking and retrieval strategies using standard IR metrics:

### Recall@K
- Measures whether relevant items appear in the top-K candidate set
- Used mainly to evaluate recall-stage effectiveness

### NDCG@K
- Measures ranking quality with position-aware relevance weighting
- Used to evaluate ranking-stage improvements

The framework allows:
- consistent evaluation across multiple experimental runs
- fair comparison under identical candidate sets

## Experiment Design

Rather than tuning a single model, I designed controlled experiments to study how different factors affect ranking quality:

### 1. Recall Size Analysis

- Varied recall set size (e.g. Top-50 / Top-100 / Top-200)
- Observed trade-offs between:
  - recall coverage
  - ranking difficulty
  - noise introduced by larger candidate pools

### 2. Negative Sampling Strategies

- Compared different negative sampling approaches in ranking data construction
- Analyzed how negative quality impacts:
  - metric stability
  - apparent ranking gains

### 3. Feature Choice Sensitivity

- Evaluated how adding or removing features affects NDCG@K
- Avoided feature combinations that produced unstable or overfitted improvements

## Ablation Studies

To validate that observed gains were meaningful, I performed ablation studies:

- Removed individual features or heuristics
- Checked whether improvements persisted across:
  - different random seeds
  - different K values

This helped distinguish:
- genuine signal improvements
- metric gains caused by overly specific heuristics

## A/B Testing Perspective (Conceptual)

This project is offline-only, but the evaluation was designed with online deployment in mind.

### What Offline Evaluation Can Do

- Compare models under controlled conditions
- Filter out clearly worse approaches
- Reduce risk before online testing

### What Offline Evaluation Cannot Guarantee

- Real user behavior alignment
- Robustness to distribution shift
- Actual business impact

In production systems, online A/B testing would be required to:
- validate user engagement improvements
- measure latency and system stability
- observe long-term effects

## Monitoring & Rollback Considerations

Although not deployed online, this project explicitly considers production safeguards:

### Metric Monitoring
- Track Recall@K / NDCG@K trends across experiments
- Detect unstable or non-generalizable improvements

### Reproducibility
- Fixed random seeds
- Consistent data splits
- Logged experiment configurations

### Rollback Mindset
- Any model or heuristic showing inconsistent gains would be reverted
- Emphasis on stable baselines over aggressive tuning

## Key Takeaways

- **Offline metrics are necessary but not sufficient**
- **Controlled experimentation is more valuable than single-run performance**
- **Ablation studies help avoid misleading improvements**
- **Online A/B testing is essential for real-world validation**

This project reflects how ranking optimization is approached before production rollout, especially in data-limited or early-stage systems.

## Limitations & Future Work

**Limitations**
- 离线评估基于模拟交互日志，难以完全反映真实线上环境中的曝光偏差与反馈延迟问题。
- 指标主要集中于 Recall@K 与 NDCG@K，未直接衡量对业务目标（如转化率或留存）的影响。
- 实验结果对负采样策略与数据切分方式较为敏感，存在一定评估偏差风险。

**Future Work**
- 引入反事实评估或日志回放（replay）机制，减少离线指标与线上效果之间的偏差。
- 在条件允许的情况下，通过线上 A/B 测试验证不同排序策略的真实收益。
- 结合多指标联合评估，避免模型仅针对单一指标过度优化。

