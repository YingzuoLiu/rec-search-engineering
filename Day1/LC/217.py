class Solution(object):
    def containsDuplicate(self, nums):
        """
        :type nums: List[int]
        :rtype: bool
        """
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False

from collections import Counter

def count_duplicate_numbers(nums):
    cnt = Counter(nums)
    res = 0
    for x in cnt:
        if cnt[x] > 1:
            res += 1
    return res
