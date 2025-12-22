class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        first = strs[0]
        for i in range(len(first)):
            for s in strs[1:]:
                if i >= len(s) or s[i] != first[i]:
                    return first[:i]
        return first
