for _ in range(int(input())):
    n = int(input())
    nums = [int(x) for x in input()]
    l = len(nums)
    TOT = [nums[i:i + n] for i in range(n)]
    ans = [1 if sum(TOT[j][i] for j in range(n)) else 0 for i in range(n)]
    print("".join(str(x) for x in ans))

