# Day 1 算法学习总结：Hash / Set / Counter

## 一、 核心主题：Hash（哈希）思想

### 1. 什么是 Hash？
Hash 是一种 **用 key 快速定位数据位置** 的方法。
* **底层实现**：Python 中的 `dict` 和 `set` 底层都是哈希表。
* **时间复杂度**：平均为 $O(1)$（最坏情况 $O(n)$，但在实际应用中极少发生）。

### 2. 什么时候用 Hash？
* 需要 **快速查找** 某个元素。
* 需要 **判断是否出现过**（去重/查重）。
* 需要 **统计频率**。
* 需要建立 **值 $\rightarrow$ 信息**（如：值 $\rightarrow$ 下标）的映射。

---

## 二、 Python 中三种常用 Hash 容器

| 容器 | 主要用途 | 典型操作 |
| :--- | :--- | :--- |
| **`set()`** | 判断是否存在、去重 | `x in seen`, `seen.add(x)` |
| **`dict {}`** | 存储映射关系（值 $\rightarrow$ 下标/信息） | `d[x] = i`, `if x in d` |
| **`Counter`** | 专门用于统计出现次数 | `cnt[x]`, `cnt[x] > 1` |

---

## 三、 经典题解：LC217. Contains Duplicate

### 1. 问题描述
判断数组中是否存在重复元素。如果任意一值在数组中出现至少两次，函数返回 `True`；如果数组中每个元素互不相同，返回 `False`。

### 2. 解题思路
使用 `set` 记录已经遍历过的数字：
1.  遍历数组，检查当前数字是否在 `seen` 集合中。
2.  如果在：说明重复，立刻返回 `True` (**Early Exit**)。
3.  如果不在：将该数字存入 `seen`。
4.  遍历结束：说明无重复，返回 `False`。



### 3. 代码实现
```python
class Solution(object):
    def containsDuplicate(self, nums):
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
```

## 四、 进阶扩展

### 1. 有多少个「不同的数」是重复的？
* **问题含义**：数组中，有多少种数字出现了不止一次？
* **示例**：`nums = [1, 2, 3, 1, 2, 2]`，其中 `1` 和 `2` 重复了，答案为 `2`。
* **思路**：使用 `Counter` 统计频次，遍历 `cnt`，如果次数 $> 1$，则计数器 `res + 1`。

```python
from collections import Counter

def count_duplicate_numbers(nums):
    cnt = Counter(nums)
    res = 0
    for x in cnt:
        if cnt[x] > 1:
            res += 1
    return res
```

### 2. 一共有多少个「重复出现的元素」？
* **问题含义**：把所有“多出来的重复部分”都算上（即非唯一的元素总量）。
* **示例**：`nums = [1, 2, 3, 1, 2, 2]`
    * `1` 出现了 2 次，多出 1 个；
    * `2` 出现了 3 次，多出 2 个；
    * 总重复次数 = $1 + 2 = 3$。
* **思路**：使用 `Counter` 统计频次，对每个数累加 `cnt[x] - 1`。

```python
def count_duplicate_occurrences(nums):
    cnt = Counter(nums)
    res = 0
    for x in cnt:
        if cnt[x] > 1:
            res += (cnt[x] - 1)
    return res
```
## 五、 Python 语法与控制流关键点

### 1. `for i, x in enumerate(nums)`
* **i**：下标（index）
* **x**：当前元素的值（value）
* **等价写法**：
    ```python
    for i in range(len(nums)):
        x = nums[i]
    ```

### 2. `:`（冒号）的作用
* 表示一个**代码块的开始**。
* 在 Python 中，所有控制流语句（`for`, `if`, `while`）和定义语句（`def`, `class`）后面都必须跟着冒号。

### 3. `return` 的作用
* **立即结束**：一旦执行到 `return`，函数会立刻停止，不再执行后面的循环或代码。
* **提前退出 (Early Exit)**：在查重问题中，只要找到一个重复，就立刻 `return True`，这比检查完整个数组要快得多。

### 4. `res` 与 `+=`
* **res**：常用变量名，`result` 的缩写。
* **`+=`**：累加操作。`res += 1` 相当于 `res = res + 1`。

---

## 六、 核心套路总结

**Hash 题通用模板：**

```python
# 1. 初始化 Hash 结构 (set, dict, 或 Counter)
memo = set() 

# 2. 遍历数据
for x in data:
    # 3. 判断“之前是否满足过条件”
    if x in memo:
        return ... # 找到目标，提前退出
    
    # 4. 记录当前元素信息到哈希表
    memo.add(x) 

# 5. 遍历结束仍未找到
return ... # 最终结论（默认值）
```
