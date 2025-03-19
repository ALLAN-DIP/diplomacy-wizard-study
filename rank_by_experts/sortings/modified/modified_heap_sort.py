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
    This function would be implemented using a 2-way comparison function.
    """
    # In a real implementation, this would be your 2-way comparison function
    # Here we're just using a simple sort as placeholder
    print("Sorting [2]", x1, x2)
    return sorted([x1, x2])

def modified_heapify(arr, n, i):
    """
    Modified heapify operation using rank comparisons instead of direct comparisons.
    This function maintains the heap property at node i.
    """
    largest = i  # Initialize largest as root
    left = 2 * i + 1  # Left child
    right = 2 * i + 2  # Right child
    
    # For traditional heapsort we'd do multiple comparisons, but here we'll use rank functions
    if left < n and right < n:
        # If both children exist, use rank3
        sorted_elements = rank3(arr[i], arr[left], arr[right])
        largest_value = sorted_elements[2]  # Get largest value (for max heap)
        
        # Find index of the largest value
        if largest_value == arr[i]:
            largest = i
        elif largest_value == arr[left]:
            largest = left
        else:
            largest = right
    elif left < n:
        # Only left child exists, use rank2
        sorted_elements = rank2(arr[i], arr[left])
        if sorted_elements[1] == arr[left]:  # If left child is larger
            largest = left
    
    # If largest is not root, swap and continue heapifying
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        modified_heapify(arr, n, largest)

def modified_build_heap(arr):
    """
    Builds a heap from an array using modified heapify.
    """
    n = len(arr)
    # Build max heap (from last non-leaf node up to root)
    for i in range(n // 2 - 1, -1, -1):
        modified_heapify(arr, n, i)

def modified_heapsort(arr):
    """
    Modified heap sort using rank comparisons instead of direct comparisons.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    if len(arr) == 2:
        return rank2(arr[0], arr[1])
    
    if len(arr) == 3:
        return rank3(arr[0], arr[1], arr[2])
    
    # Make a copy of the array to avoid modifying the original
    heap = arr.copy()
    n = len(heap)
    
    # Build a max heap
    modified_build_heap(heap)
    
    # Extract elements one by one
    result = []
    for i in range(n-1, 0, -1):
        # Move current root to the end
        heap[0], heap[i] = heap[i], heap[0]
        result.append(heap[i])
        # Call heapify on the reduced heap
        modified_heapify(heap, i, 0)
    
    # Add the last element
    result.append(heap[0])
    
    # Return the result in reverse (as we built a max heap)
    return result[::-1]

def modified_heapsort_optimized(arr):
    """
    An optimized version of modified heap sort that minimizes comparisons
    by using 4-way comparisons where possible.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    if len(arr) == 2:
        return rank2(arr[0], arr[1])
    
    if len(arr) == 3:
        return rank3(arr[0], arr[1], arr[2])
    
    # Create a copy to avoid modifying the original array
    heap = arr.copy()
    n = len(heap)
    
    # Build the heap structure using 4-way comparisons where possible
    for i in range(n // 4 - 1, -1, -1):
        # Try to process four nodes at once
        parent = i
        children = [4*i+1, 4*i+2, 4*i+3, 4*i+4]
        valid_children = [idx for idx in children if idx < n]
        
        if len(valid_children) == 3:
            # 4 nodes (parent + 3 children)
            values = [heap[parent], heap[valid_children[0]], heap[valid_children[1]], heap[valid_children[2]]]
            sorted_values = rank4(*values)
            # Place the largest at the parent position
            largest_value = sorted_values[3]
            largest_idx = values.index(largest_value)
            if largest_idx != 0:  # If parent is not the largest
                if largest_idx == 1:
                    heap[parent], heap[valid_children[0]] = heap[valid_children[0]], heap[parent]
                    modified_heapify(heap, n, valid_children[0])
                elif largest_idx == 2:
                    heap[parent], heap[valid_children[1]] = heap[valid_children[1]], heap[parent]
                    modified_heapify(heap, n, valid_children[1])
                else:
                    heap[parent], heap[valid_children[2]] = heap[valid_children[2]], heap[parent]
                    modified_heapify(heap, n, valid_children[2])
        else:
            # Fall back to traditional heapify for nodes with fewer children
            modified_heapify(heap, n, i)
    
    # Complete the build process for any remaining nodes
    for i in range((n // 4) * 4 - 1, -1, -1):
        if i not in range(n // 4 - 1, -1, -1):
            modified_heapify(heap, n, i)
    
    # Extract elements in sorted order
    result = []
    for i in range(n-1, 0, -1):
        heap[0], heap[i] = heap[i], heap[0]  # Swap root with last element
        result.append(heap[i])
        modified_heapify(heap, i, 0)  # Heapify the reduced heap
    
    result.append(heap[0])  # Add the final element
    return result[::-1]  # Reverse to get ascending order

# Example usage
def test_modified_heapsort():
    random.seed(0)
    test_arr = random.sample(range(100), 45)
    # print("\nRunning basic modified heapsort:")
    # sorted_arr1 = modified_heapsort(test_arr)
    # print("Sorted array (basic):", sorted_arr1)
    
    # print("\nRunning optimized modified heapsort:")
    sorted_arr2 = modified_heapsort_optimized(test_arr)
    print("Original array:", test_arr)
    print("Sorted array (optimized):", sorted_arr2)
    assert sorted_arr2 == sorted(test_arr)

if __name__ == "__main__":
    test_modified_heapsort()
