import random
import asyncio
import httpx

async def rank_k(*arr):
    """
    Requests user ranking via API and waits until the user provides a response.
    """
    async with httpx.AsyncClient() as client:
        # Notify the server of the elements to rank
        await client.post("http://127.0.0.1:8000/ranking/task", json={"elements": list(arr)})

        print(f"Waiting for user input to rank: {arr}")

        # Wait until the user submits an order
        while True:
            order_response = await client.get("http://127.0.0.1:8000/ranking/response")
            response_json = order_response.json()
            if "sorted_order" in response_json:
                break  # Order is received, proceed

            await asyncio.sleep(1)  # Polling every second

        # Get the final sorted order
        sorted_arr = response_json["sorted_order"]

    print(f"User provided order: {sorted_arr}")
    return sorted_arr

async def modified_quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    if len(arr) <= 3:
        return await rank_k(*arr)

    n = len(arr)
    pivot_indices = [0, n // 2, n - 1]
    pivots = await rank_k(*[arr[i] for i in pivot_indices])

    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []

    for element in [arr[i] for i in range(n) if i not in pivot_indices]:
        sorted_elements = await rank_k(element, pivots[0], pivots[1], pivots[2])
        element_index = sorted_elements.index(element)
        if element_index == 0:
            less_than_pivot1.append(element)
        elif element_index == 1:
            between_pivot1_and_pivot2.append(element)
        elif element_index == 2:
            between_pivot2_and_pivot3.append(element)
        else:
            greater_than_pivot3.append(element)

    sorted_less = await modified_quicksort(less_than_pivot1)
    sorted_between1_2 = await modified_quicksort(between_pivot1_and_pivot2)
    sorted_between2_3 = await modified_quicksort(between_pivot2_and_pivot3)
    sorted_greater = await modified_quicksort(greater_than_pivot3)

    return sorted_less + [pivots[0]] + sorted_between1_2 + [pivots[1]] + sorted_between2_3 + [pivots[2]] + sorted_greater

async def test_modified_quicksort():
    random.seed(0)
    test_arr = random.sample(range(100), 5)

    sorted_arr = await modified_quicksort(test_arr)

    print("Original array:", test_arr)
    print("Sorted array:", sorted_arr)
    assert sorted_arr == sorted(test_arr)

asyncio.run(test_modified_quicksort())
