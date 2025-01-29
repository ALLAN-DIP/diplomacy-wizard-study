import json
import os


def order_key_orders(alter):
    unit = ' '.join(alter[0].split(' ')[:2])
    prob = alter[1]
    return unit, prob


def rescale_sort(alters):
    alters_cpy = alters.copy()
    for order, prob in alters_cpy.items():
        alters[order] = prob / max([prob for order_, prob in alters_cpy.items() if ' '.join(order.split(' ')[:2]) == ' '.join(order_.split(' ')[:2])])
    return sorted([[x, y] for x, y in alters.items()], key=order_key_orders, reverse=True)


def get_alterations(moves):
    alternations = {power: {} for power in moves}
    for power, moves_struct in moves.items():
        alters = {}
        for orders_struct in moves_struct:
            orders, prob = orders_struct
            for order in orders:
                if order not in alters: # getting the max prob for each order in all order sets
                    alters[order] = prob
                elif prob > alters[order]:
                    alters[order] = prob
        alternations[power] = rescale_sort(alters)
    return alternations


for filename in os.listdir('.'):
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            data = json.load(f)
        data['alterations'] = get_alterations(data['moves'])
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)