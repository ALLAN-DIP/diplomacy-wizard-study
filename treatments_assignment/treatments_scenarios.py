import pandas as pd
from itertools import product
import random

TYPES = ["null", "sugg-TB", "sugg-TKT", "sugg-VB", "sugg-VKT"]
SIDE = ["null", "side-self", "side-other", "both"]
FRICTION = ["null", "YCO", "ROO", "ERO"]

# in total, there are 80 combinations
# but not all combinations are valid

# invalid combinations:
# if type is null, side must be null, friction could be only ERO or null
# if type is not null, side must be a not null item, friction could be null, YCO, ROO, ERO
# if friction is YCO or ROO, side must be side-self or both

# then we would have 42 valid combinations
# because of symmetry, we can remove N-N-ERO
# also N-N-N is handled under delayed cases
# therefor we have 40 combinations
treatments = {
    "type": [],
    "side": [],
    "friction": []
}
for t, s, f in product(TYPES, SIDE, FRICTION):
    if t == "null":
        if s != "null" or f not in ["null", "ERO"]:
            continue
    else:
        if s == "null":
            continue
        if f in ["YCO", "ROO"] and s not in ["side-self", "both"]:
            continue
    t_str = "null" if t == "null" else t.replace("sugg-", "")
    s_str = "null" if s == "null" else s.replace("side-", "")
    f_str = f
    print(f"{t_str} {s_str} {f_str}")
    if t_str == "null" and s_str == "null" and f_str in ["null", "ERO"]:
        continue
    treatments["type"].append(t)
    treatments["side"].append(s)
    treatments["friction"].append(f)

treatments_df = pd.DataFrame(treatments)
treatments_df.to_csv("treatments.csv", index=False)
print("length of treatments:", len(treatments_df))

SCENARIO_IDs = [1, 2, 3, 4]
participants_assignments = {
    "participant_id": [],
    "scenario1": [], # the scenario which appeared first
    "type1": [],
    "side1": [],
    "friction1": [],
    "scenario2": [], # the scenario which appeared second
    "type2": [],
    "side2": [],
    "friction2": [],
    "scenario3": [], # the scenario which appeared third
    "type3": [],
    "side3": [],
    "friction3": [],
    "scenario4": [], # the scenario which appeared fourth
    "type4": [],
    "side4": [],
    "friction4": [],
}

random.seed(0)
