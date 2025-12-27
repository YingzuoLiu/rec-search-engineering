# BFS 分层模板总结

**当需要"一层一层处理数据"时，用 BFS 分层模板。**

## 关键词

- 分层
- 分阶段
- 不混顺序
- 批处理

## 适用场景

在代码或需求里看到这些词，就想到这个模板：

- **层 / stage / phase**
- **pipeline / fallback**
- **逐级扩散 / 传播**
- **父 → 子 / 上 → 下**

👉 不只是树，**任何"层级结构"都适用**

## Tree BFS 模板

```python
from collections import deque

def tree_bfs_template(root):
    if not root:
        return []
    
    res = []
    queue = deque([root])
    
    while queue:
        level = []
        level_size = len(queue)
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)  # ① 处理当前节点
            
            if node.left:  # ② 扩展下一层
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        res.append(level)  # ③ 当前层结束
    
    return res
```

## 模板关键步骤解析

### 1️⃣ queue = deque([root])

- 初始化第一层
- root = 起点 / 初始任务 / 顶层节点

### 2️⃣ while queue:

- **还有没处理完的层**
- 系统还没结束

### 3️⃣ level_size = len(queue)

在进入这一层之前，  
**先"数清楚这一层有多少个元素"**

工程意义：
- 固定 batch
- 防止下一层混进来
- 保证阶段边界清晰

### 4️⃣ for _ in range(level_size):

- **只处理当前层**
- 不多、不少

### 5️⃣ queue.popleft()

- 按发现顺序处理
- FIFO（先进先出）

### 6️⃣ queue.append(child)

- 不立刻处理
- 放到**下一层**

### 7️⃣ res.append(level)

- 当前阶段结束
- 输出一个"层级结果"

## 模板的"不变量"

只要是**正确的分层 BFS**，一定满足这 5 条：

1. ✅ 用 deque
2. ✅ while queue
3. ✅ 先 level_size = len(queue)
4. ✅ for _ in range(level_size)
5. ✅ 当前层和下一层严格分开

**少一条 = 不是标准分层 BFS**

## 把模板迁移到"非树"场景

你只改三件事：

| **树 BFS** | **业务 BFS** |
|------------|--------------|
| node | task / item / stage |
| left / right | next_items |
| node.val | 业务字段 |

**骨架完全不变**

```python
queue = deque([start])

while queue:
    level = []
    size = len(queue)
    
    for _ in range(size):
        x = queue.popleft()
        level.append(process(x))
        queue.extend(next_items(x))
    
    res.append(level)
```

## 总结

"tree BFS 的核心不是树，而是**分层处理**。通过在每一轮先固定 queue 的 size，可以确保当前层和下一层严格分离，这种模式在工程里的 pipeline、fallback 和阶段控制中非常常见。"
