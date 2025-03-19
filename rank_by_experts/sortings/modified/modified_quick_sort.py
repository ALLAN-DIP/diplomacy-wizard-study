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

def modified_quicksort(arr):
    """
    Modified quicksort using 3 pivot elements and a 4-way comparator.
    """
    if len(arr) <= 1:
        return arr
    
    if len(arr) == 2:
        return rank2(arr[0], arr[1])
    
    if len(arr) == 3:
        return rank3(arr[0], arr[1], arr[2])
    
    # Select 3 pivot elements
    # For simplicity, we'll pick first, middle, and last elements
    # In practice, you might want a more sophisticated pivot selection
    n = len(arr)
    pivot_indices = [0, n // 2, n - 1]
    pivots = [arr[i] for i in pivot_indices]
    
    # Sort the pivots (this is just to make the partitioning logic cleaner)
    pivots = rank3(pivots[0], pivots[1], pivots[2])
    
    # Initialize four partitions
    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []
    
    # Partition the array into four groups
    # We'll exclude the original pivot elements from this process
    remaining_elements = [arr[i] for i in range(n) if i not in pivot_indices]
    
    for element in remaining_elements:
        # Use the 4-way comparator to determine which partition this element belongs to
        sorted_elements = rank4(element, pivots[0], pivots[1], pivots[2])
        
        # Determine the position of the element relative to the pivots
        element_index = sorted_elements.index(element)
        
        if element_index == 0:
            less_than_pivot1.append(element)
        elif element_index == 1:
            between_pivot1_and_pivot2.append(element)
        elif element_index == 2:
            between_pivot2_and_pivot3.append(element)
        else:  # element_index == 3
            greater_than_pivot3.append(element)
    
    # Recursively sort each partition
    sorted_less = modified_quicksort(less_than_pivot1)
    sorted_between1_2 = modified_quicksort(between_pivot1_and_pivot2)
    sorted_between2_3 = modified_quicksort(between_pivot2_and_pivot3)
    sorted_greater = modified_quicksort(greater_than_pivot3)
    
    # Combine the sorted partitions and the pivots
    return sorted_less + [pivots[0]] + sorted_between1_2 + [pivots[1]] + sorted_between2_3 + [pivots[2]] + sorted_greater

# Example usage
def test_modified_quicksort():
    random.seed(0)
    test_arr = random.sample(range(100), 45)
    sorted_arr = modified_quicksort(test_arr)
    print("Original array:", test_arr)
    print("Sorted array:", sorted_arr)
    assert sorted_arr == sorted(test_arr)

test_modified_quicksort()