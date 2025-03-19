import random


def rank4(x1, x2, x3, x4):
    """
    Sorts four elements and returns them in increasing order.
    This function would be implemented using a 4-way comparator.
    """
    # In a real implementation, this would be your 4-way comparison function
    # Here we're just using a simple sort as placeholder
    print("Sorting [4]", x1, x2, x3, x4)
    return sorted([x1, x2, x3, x4])

def rank3(x1, x2, x3):
    """
    Sorts three elements and returns them in increasing order.
    This function would be implemented using a 3-way comparator.
    """
    # In a real implementation, this would be your 3-way comparison function
    # Here we're just using a simple sort as placeholder
    print("Sorting [3]", x1, x2, x3)
    return sorted([x1, x2, x3])

def rank2(x1, x2):
    """
    Sorts two elements and returns them in increasing order.
    This function would be implemented using a 2-way comparator.
    """
    # In a real implementation, this would be your 2-way comparison function
    # Here we're just using a simple sort as placeholder
    print("Sorting [2]", x1, x2)
    return sorted([x1, x2])

def modified_merge(left, right):
    """
    Merges two sorted arrays using rank functions instead of direct comparisons.
    """
    result = []
    i, j = 0, 0
    
    while i < len(left) and j < len(right):
        # Use rank2 to compare elements from both arrays
        sorted_pair = rank2(left[i], right[j])
        
        if sorted_pair[0] == left[i]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

def modified_merge_optimized(left, right):
    """
    Optimized merge function that uses rank4 where possible to reduce comparisons.
    """
    result = []
    i, j = 0, 0
    
    # Process elements in groups of 2 from each array where possible
    while i + 1 < len(left) and j + 1 < len(right):
        # Use rank4 to compare 2 elements from each array
        sorted_elements = rank4(left[i], left[i+1], right[j], right[j+1])
        
        # Extract the smallest two elements
        for element in sorted_elements[:2]:
            result.append(element)
            if element in [left[i], left[i+1]]:
                if element == left[i]:
                    i += 1
                else:
                    i += 1
                    # Adjust if we've processed out of order
                    if i <= len(left) - 1 and left[i-1] == left[i]:
                        i += 1
            else:
                if element == right[j]:
                    j += 1
                else:
                    j += 1
                    # Adjust if we've processed out of order
                    if j <= len(right) - 1 and right[j-1] == right[j]:
                        j += 1
    
    # Handle remaining elements using regular merge
    while i < len(left) and j < len(right):
        sorted_pair = rank2(left[i], right[j])
        if sorted_pair[0] == left[i]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add any remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

def modified_merge_sort(arr):
    """
    Basic modified merge sort using rank functions.
    """
    if len(arr) <= 1:
        return arr
    
    if len(arr) == 2:
        return rank2(arr[0], arr[1])
    
    if len(arr) == 3:
        return rank3(arr[0], arr[1], arr[2])
    
    # Divide the array into two halves
    mid = len(arr) // 2
    left = modified_merge_sort(arr[:mid])
    right = modified_merge_sort(arr[mid:])
    
    # Merge the sorted halves
    return modified_merge(left, right)

def modified_merge_sort_optimized(arr):
    """
    Optimized modified merge sort that uses 4-way comparisons where possible.
    """
    if len(arr) <= 1:
        return arr
    
    if len(arr) == 2:
        return rank2(arr[0], arr[1])
    
    if len(arr) == 3:
        return rank3(arr[0], arr[1], arr[2])
    
    if len(arr) == 4:
        return rank4(arr[0], arr[1], arr[2], arr[3])
    
    # For larger arrays, divide into 4 parts where possible
    if len(arr) >= 8:
        quarter = len(arr) // 4
        first_quarter = modified_merge_sort_optimized(arr[:quarter])
        second_quarter = modified_merge_sort_optimized(arr[quarter:2*quarter])
        third_quarter = modified_merge_sort_optimized(arr[2*quarter:3*quarter])
        fourth_quarter = modified_merge_sort_optimized(arr[3*quarter:])
        
        # Merge in pairs
        first_half = modified_merge_optimized(first_quarter, second_quarter)
        second_half = modified_merge_optimized(third_quarter, fourth_quarter)
        
        # Final merge
        return modified_merge_optimized(first_half, second_half)
    else:
        # Fall back to binary split for smaller arrays
        mid = len(arr) // 2
        left = modified_merge_sort_optimized(arr[:mid])
        right = modified_merge_sort_optimized(arr[mid:])
        return modified_merge_optimized(left, right)

# Example usage
def test_modified_merge_sort():
    random.seed(0)
    test_arr = random.sample(range(100), 45)
    # print("\nRunning basic modified merge sort:")
    # sorted_arr1 = modified_merge_sort(test_arr)
    # print("Sorted array (basic):", sorted_arr1)
    
    # print("\nRunning optimized modified merge sort:")
    sorted_arr2 = modified_merge_sort_optimized(test_arr)
    print("Original array:", test_arr)
    print("Sorted array (optimized):", sorted_arr2)
    assert sorted_arr2 == sorted(test_arr)

if __name__ == "__main__":
    test_modified_merge_sort()
