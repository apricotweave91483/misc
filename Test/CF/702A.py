n = int(input())
nums = list(map(float, input().split()))

curr_min = nums[0]
cnt = 1
cntmz = 1

for i in range(1, len(nums)):
    if nums[i] > nums[i - 1]:
        cnt += 1
    else:
        cnt = 1
    cntmz = max(cnt, cntmz)
print(cntmz)
