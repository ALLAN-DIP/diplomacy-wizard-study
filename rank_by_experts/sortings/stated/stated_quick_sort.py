import random

def rank_k(*arr):
    """
    Sorts k elements and returns them in increasing order.
    This function would be implemented using a k-way comparator.
    """
    # In a real implementation, this would be your k-way comparison function
    # Here we're just using a simple sort as placeholder
    print(f"Sorting [{len(arr)}]", *arr)
    return sorted(arr)

def modified_quicksort(arr):
    """
    Modified quicksort using 3 pivot elements and a 4-way comparator.
    """
    if len(arr) <= 1:
        return arr
    
    if len(arr) <= 3:
        return rank_k(*arr)

    n = len(arr)
    pivot_indices = [0, n // 2, n - 1]
    pivots = rank_k(*[arr[i] for i in pivot_indices])

    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []

    for element in [arr[i] for i in range(n) if i not in pivot_indices]:
        sorted_elements = rank_k(element, pivots[0], pivots[1], pivots[2])
        
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

    sorted_less = modified_quicksort(less_than_pivot1)
    sorted_between1_2 = modified_quicksort(between_pivot1_and_pivot2)
    sorted_between2_3 = modified_quicksort(between_pivot2_and_pivot3)
    sorted_greater = modified_quicksort(greater_than_pivot3)

    return sorted_less + [pivots[0]] + sorted_between1_2 + [pivots[1]] + sorted_between2_3 + [pivots[2]] + sorted_greater

def test_modified_quicksort():
    random.seed(0)
    test_arr = random.sample(range(100), 45)
    sorted_arr = modified_quicksort(test_arr)
    print("Original array:", test_arr)
    print("Sorted array:", sorted_arr)
    assert sorted_arr == sorted(test_arr)

test_modified_quicksort()
