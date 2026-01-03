class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        n = len(nums)
        cnt = {}
        for x in nums:
            if x not in cnt:
                cnt[x] = 1
            else:
                cnt[x] += 1
            if cnt[x] > n//2:
                return x
