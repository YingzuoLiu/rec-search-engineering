class Solution(object):
    def isValid(self, s):
        """
        :type s: str
        :rtype: bool
        """
        mp = {')':'(',']':'[','}':'{'}
        stack = []
        for ch in s:
            if ch in mp:
                if not stack or stack[-1] != mp[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)
        return len(stack) == 0
