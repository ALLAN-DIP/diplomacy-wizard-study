import sys
import json

DEFAULT_HOMES = [
    "EDI",
    "LVP",
    "LON",
    "STP",
    "MOS",
    "WAR",
    "SEV",
    "BUD",
    "ANK",
    "CON",
    "SMY",
    "VIE",
    "TRI",
    "VEN",
    "ROM",
    "NAP",
    "TUN",
    "MAR",
    "MUN",
    "BER",
    "KIE",
    "PAR",
    "BRE",
]

incomplete_json = sys.argv[1]
with open(incomplete_json, 'r') as f:
    data = json.load(f)

for i, phase in enumerate(data['phases']):
    phase = phase['state']
    units = phase['units']
    centers = phase['centers']
    _homes = phase['homes']
    _influence = phase['influence']
    for power, home in _homes.items():
        _homes[power] = list(set(DEFAULT_HOMES).intersection(centers[power]))
    for power, influence in _influence.items():
        units_power = [x.split(' ')[1] for x in units[power]]
        _influence[power] = list(set(centers[power]).union(set(units_power)))
    data['phases'][i]['state']['homes'] = _homes
    data['phases'][i]['state']['influence'] = _influence

with open(incomplete_json, 'w') as f:
    json.dump(data, f, indent=4)
