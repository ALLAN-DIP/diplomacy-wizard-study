import sys
import os
import json
import shutil

path2svg_dir = sys.argv[1]
path2svg_dir_best = path2svg_dir + '-bests'
path2scenario = sys.argv[2]

rand_i, phase, power = path2scenario.split('/')[-1].split('-')
rand_i = int(rand_i.split('rand')[-1])
path2json_phase = os.path.join(path2scenario, f'rand{rand_i}-{phase}.json')

with open(path2json_phase, 'r') as f:
    json_phase = json.load(f)


units = json_phase['state']['units']
for unit in units[power]:
    unit_str = unit.replace(' ', '_')

    path2svg = os.path.join(path2svg_dir, f'output_{rand_i}_{phase}_{unit_str}.svg')
    shutil.copy(path2svg, path2scenario)
    print(f'Copied {path2svg} to {path2scenario}')

    path2svg = os.path.join(path2svg_dir_best, f'output_{rand_i}_{phase}_{unit_str}.svg')
    shutil.copyfile(path2svg, os.path.join(path2scenario, f'output_{rand_i}_{phase}_{unit_str}_BEST.svg'))
    print(f'Copied {path2svg} to {path2scenario}')

path2svg_empty = os.path.join(path2svg_dir, f'output_{rand_i}_{phase}.svg')
shutil.copy(path2svg_empty, path2scenario)
print(f'Copied {path2svg_empty} to {path2scenario}')

path2svg_power = os.path.join(path2svg_dir, f'output_{rand_i}_{phase}_{power}.svg')
shutil.copy(path2svg_power, path2scenario)

path2svg_power = os.path.join(path2svg_dir_best, f'output_{rand_i}_{phase}_{power}.svg')
shutil.copyfile(path2svg_power, os.path.join(path2scenario, f'output_{rand_i}_{phase}_{power}_BEST.svg'))
print(f'Copied {path2svg_power} to {path2scenario}')

with open(os.path.join(path2svg_dir, f'output_{rand_i}_{phase}.json')) as f:
    order_json = json.load(f)
    for p, o in order_json['alterations'].items():
        if p == power:
            continue
        order_json['alterations'][p] = []
    with open(os.path.join(path2scenario, 'data.json'), 'w') as f:
        json.dump(order_json, f, indent=4)
        print(f'Copied data.json to {path2scenario}')
