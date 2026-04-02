import heapq

def merge_retrieval_results(streams, topk=5):
    heap = []
    results = []
    seen = set()

    # 1) 初始化：每一路先放一个
    for sid, stream in enumerate(streams):
        if stream:
            doc = stream[0]
            heapq.heappush(
                heap,
                (-doc["score"], sid, 0, doc)
            )

    # 2) 不断取全局最优
    while heap and len(results) < topk:
        neg_score, sid, idx, doc = heapq.heappop(heap)

        # 3) 去重
        if doc["id"] not in seen:
            seen.add(doc["id"])
            results.append(doc)

        # 4) 推进当前 source 的下一条
        next_idx = idx + 1
        if next_idx < len(streams[sid]):
            next_doc = streams[sid][next_idx]
            heapq.heappush(
                heap,
                (-next_doc["score"], sid, next_idx, next_doc)
            )

    return results

"""
heap 始终维护每一路当前最优 head candidate
每次弹出全局最高分
然后只推进该路下一条继续参与竞争
同时做 duplicate removal
直到拿够 topK
"""
