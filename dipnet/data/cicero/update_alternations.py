import json
import os


def order_key_orders(alter):
    unit = ' '.join(alter[0].split(' ')[:2])
    prob = alter[1]
    return unit, prob


def get_alterations(moves):
    alternations = {power: {} for power in moves}
    for power, moves_struct in moves.items():
        alters = []
        for orders_struct in moves_struct:
            orders, prob = orders_struct
            for order in orders:
                alters.append([order, prob])
        alternations[power] = sorted(alters, key=order_key_orders, reverse=True)
    return alternations


for filename in os.listdir('.'):
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            data = json.load(f)
        data['alterations'] = get_alterations(data['moves'])
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)