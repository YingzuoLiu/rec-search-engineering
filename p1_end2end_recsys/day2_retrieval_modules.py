# 1) 数据结构（用户 / 商家 / 上下文）
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import random
import time

@dataclass(frozen=True)
class User:
    user_id: str
    city: str
    is_new_user: bool
    is_high_value: bool  # 模拟“高价值用户”

@dataclass(frozen=True)
class Context:
    hour: int  # 0~23
    device: str  # "android" / "ios"

@dataclass
class Merchant:
    merchant_id: str
    city: str
    is_open: bool
    is_new_merchant: bool
    rating: float          # 1~5
    eta_min: int           # 配送 ETA
    price_level: int       # 1~3
    promo: bool            # 是否活动

# 2) Cohort：新用户怎么分群（冷启动 proxy）
def cohort_key(user: User, ctx: Context) -> str:
    """把用户分到一个 cohort（可观测分群）"""
    daypart = "breakfast" if 6 <= ctx.hour < 10 else \
              "lunch" if 10 <= ctx.hour < 14 else \
              "dinner" if 17 <= ctx.hour < 21 else "other"
    return f"{user.city}|{daypart}|{ctx.device}"


#新用户没历史，就用 cohort 的群体偏好顶一下。

# 3) Retrieval：多路召回（规则 / 历史 / “embedding” 模拟 / 新商家路径）
def recall_popular_nearby(user: User, ctx: Context, all_merchants: List[Merchant], k: int) -> List[Merchant]:
    """规则召回：同城、开店、按 rating/ETA 简单排"""
    cands = [m for m in all_merchants if m.city == user.city and m.is_open]
    cands.sort(key=lambda m: (-m.rating, m.eta_min))
    return cands[:k]

def recall_user_history(user: User, ctx: Context, all_merchants: List[Merchant], k: int) -> List[Merchant]:
    """历史召回：这里用随机模拟；真实情况是 user 最近点击/下单商家"""
    # 演示：从同城开店里随机抽 k 个
    cands = [m for m in all_merchants if m.city == user.city and m.is_open]
    random.shuffle(cands)
    return cands[:k]

def recall_embedding_ann(user: User, ctx: Context, all_merchants: List[Merchant], k: int) -> List[Merchant]:
    """embedding ANN 召回（这里用随机 + 简单偏好模拟，不依赖 FAISS 也能演示流程）"""
    cands = [m for m in all_merchants if m.city == user.city and m.is_open]
    # 模拟：晚餐更偏好低 ETA + 有 promo
    def pseudo_sim(m: Merchant) -> float:
        base = 0.0
        base += (1.0 if m.promo else 0.0)
        base += max(0, 30 - m.eta_min) / 30.0
        base += (m.rating - 3.0)
        return base + random.random() * 0.1
    cands.sort(key=pseudo_sim, reverse=True)
    return cands[:k]

def recall_new_merchants(user: User, ctx: Context, all_merchants: List[Merchant], k: int) -> List[Merchant]:
    """新商家独立召回路径：保证新商家有基础曝光机会"""
    cands = [m for m in all_merchants if m.city == user.city and m.is_open and m.is_new_merchant]
    # 简单质量门槛：rating 太低的不召回
    cands = [m for m in cands if m.rating >= 3.8]
    cands.sort(key=lambda m: (-m.rating, m.eta_min))
    return cands[:k]

# 4) Merge / Dedup：合并多路召回、去重、截断总 K
def merge_and_dedup(recall_lists: List[List[Merchant]], max_candidates: int) -> List[Merchant]:
    seen = set()
    merged: List[Merchant] = []
    for lst in recall_lists:
        for m in lst:
            if m.merchant_id in seen:
                continue
            seen.add(m.merchant_id)
            merged.append(m)
            if len(merged) >= max_candidates:
                return merged
    return merged

# 5) Ranking：轻量打分（能跑起来就行）
def rank_score(user: User, ctx: Context, m: Merchant) -> float:
    """模拟一个 rank 模型分数：偏高评分、低 ETA、活动"""
    s = 0.0
    s += (m.rating - 3.0) * 1.2
    s += (1.0 if m.promo else 0.0) * 0.6
    s += max(0, 35 - m.eta_min) / 35.0
    # 高价值用户更在意体验：对 ETA 更敏感
    if user.is_high_value:
        s += max(0, 30 - m.eta_min) / 30.0 * 0.3
    return s

def rank_candidates(user: User, ctx: Context, cands: List[Merchant], topn: int) -> List[Tuple[Merchant, float]]:
    scored = [(m, rank_score(user, ctx, m)) for m in cands]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:topn]

# 6) Re-rank：新商家探索（比例控制 + 分群）

# “别在 rank 里强行加权，而是在 re-rank 做可控策略”。

def rerank_with_new_merchant_exploration(
    user: User,
    ranked: List[Tuple[Merchant, float]],
    topn: int,
    max_new_in_topn: int,
) -> List[Tuple[Merchant, float]]:
    """
    把新商家插入 TopN，但限制数量（可控、可回滚）。
    """
    result: List[Tuple[Merchant, float]] = []
    new_cnt = 0

    for m, s in ranked:
        if len(result) >= topn:
            break
        if m.is_new_merchant:
            if new_cnt >= max_new_in_topn:
                continue
            new_cnt += 1
        result.append((m, s))
    return result


# 分群策略（高价值用户更保守，新用户更激进）：

def decide_max_new(user: User) -> int:
    if user.is_high_value:
        return 1
    if user.is_new_user:
        return 3
    return 2

# 7) Feature Flag + Rollback：一键开关策略（模拟线上回滚）
class Flags:
    def __init__(self):
        self.enable_new_merchant_path = True
        self.enable_ann_recall = True
        self.enable_rerank_exploration = True

FLAGS = Flags()

# 8) 把全流程串起来跑
def recommend(user: User, ctx: Context, all_merchants: List[Merchant]) -> List[Tuple[Merchant, float]]:
    # 1) retrieval / recall
    recalls = []
    recalls.append(recall_popular_nearby(user, ctx, all_merchants, k=200))
    recalls.append(recall_user_history(user, ctx, all_merchants, k=200))

    if FLAGS.enable_ann_recall:
        recalls.append(recall_embedding_ann(user, ctx, all_merchants, k=200))

    if FLAGS.enable_new_merchant_path:
        recalls.append(recall_new_merchants(user, ctx, all_merchants, k=80))

    # 2) merge/dedup
    cands = merge_and_dedup(recalls, max_candidates=600)

    # 3) ranking
    ranked = rank_candidates(user, ctx, cands, topn=100)

    # 4) re-rank (exploration)
    if FLAGS.enable_rerank_exploration:
        max_new = decide_max_new(user)
        ranked = rerank_with_new_merchant_exploration(user, ranked, topn=20, max_new_in_topn=max_new)
    else:
        ranked = ranked[:20]

    return ranked

