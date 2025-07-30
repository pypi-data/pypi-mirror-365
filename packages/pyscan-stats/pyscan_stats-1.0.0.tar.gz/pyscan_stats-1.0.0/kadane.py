import math
from collections import deque

def kadane_unrestricted(weights):
    print("=== Unrestricted Kadane ===")
    max_sum = float("-inf")
    curr_sum = 0
    start = 0
    best = (0, 0)

    for end, val in enumerate(weights):
        if curr_sum <= 0:
            curr_sum = val
            start = end
        else:
            curr_sum += val

        print(f"curr_sum={curr_sum}, start={start}, end={end}")
        if curr_sum > max_sum:
            max_sum = curr_sum
            best = (start, end)

    print(f"Best subarray: {best} with sum {max_sum}\n")
    return best, max_sum

def kadane_area_limited(weights, max_height):
    print("=== Area-Limited Kadane (post-check) ===")
    max_sum = float("-inf")
    curr_sum = 0
    start = 0
    best = (0, 0)

    for end, val in enumerate(weights):
        
        height = end - start + 1
        curr_sum += val
        
        if curr_sum <= 0:
            curr_sum = val
            start = end
            continue
            

        print(f"curr_sum={curr_sum}, height={height}, start={start}, end={end}")
        if height <= max_height and curr_sum > max_sum:
            max_sum = curr_sum
            best = (start, end)

    print(f"Best subarray: {best} with sum {max_sum}\n")
    return best, max_sum

def kadane_area_improved(weights, max_height):
    print("=== Improved Area-Limited Kadane (sliding window) ===")
    max_sum = float("-inf")
    curr_sum = 0
    start = 0
    best = (0, 0)

    for end, val in enumerate(weights):
        curr_sum += val
        height = end - start + 1

        while height > max_height:
            print(f"Shrinking: height={height} > {max_height}")
            curr_sum -= weights[start]
            start += 1
            height = end - start + 1

        print(f"curr_sum={curr_sum}, height={height}, start={start}, end={end}")
        if curr_sum > max_sum:
            max_sum = curr_sum
            best = (start, end)

    print(f"Best subarray: {best} with sum {max_sum}\n")
    return best, max_sum

def kadane_with_max_len(arr, L):
    """
    Max subarray sum with length <= L.
    Returns (best_sum, (start, end)).
    """

    n = len(arr)
    prefix_sum = [0] * (n + 1)  # size n+1
    for i in range(len(prefix_sum) - 1):  # 0 to n-1
        prefix_sum[i + 1] = prefix_sum[i] + arr[i]

    dq = deque([])
    max_sum = -math.inf
    best_seg = (0, 0)

    for i in range(0, len(prefix_sum)):

        print(f"i={i}, dq={list(dq)}")

        if dq and i - dq[0] > L:
            print(f"Removing {dq[0]} from deque because length exceeds {L}")
            dq.popleft()
        
        while dq and prefix_sum[dq[-1]] > prefix_sum[i]:
            print(f"Removing {dq[-1]} from deque because prefix_sum is larger than {prefix_sum[i]}")
            dq.pop()

        if dq and prefix_sum[i] - prefix_sum[dq[0]] > max_sum:
            print(f"New max found: {prefix_sum[i]} - {prefix_sum[dq[0]]} = {prefix_sum[i] - prefix_sum[dq[0]]}")
            max_sum = prefix_sum[i] - prefix_sum[dq[0]]
            best_seg = (dq[0], i - 1)
        
        print(f"Added {i} to deque, current deque: {list(dq)}")
        dq.append(i)

    print(f"Best subarray: {best_seg} with sum {max_sum}\n")
    return max_sum, best_seg


if __name__ == "__main__":
    weights = [3, -1, 5, -7, ]
    correct = 5
    max_height = 2

    b, m = kadane_unrestricted(weights)
    b, m = kadane_area_limited(weights, max_height)
    b, m = kadane_area_improved(weights, max_height)
    b, m = kadane_with_max_len(weights, max_height)
