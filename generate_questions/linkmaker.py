import pandas as pd

# Read the input CSV
ps2link_df = pd.read_csv('Q-maps - PS2Links.csv')

# Define the base URL template
BASE_LINK = (
    "https://usc.qualtrics.com/jfe/form/SV_5ANvI3dIu0fryXs"
    "?side1={side1}&friction1={friction1}"
    "&side2={side2}&friction2={friction2}"
    "&side3={side3}&friction3={friction3}"
    "&side4={side4}&friction4={friction4}"
)


SIDE_MAP = {
    'S': 'side-self',
    'O': 'side-other',
    'SO': 'both'
}
FRICTION_MAP = {
    'N': 'null',
    'YCO': 'YCO',
    'ERO': 'ERO',
    'ROO': 'ROO',
}

def parse_scenario(s):
    if pd.isna(s) or "-" not in s:
        return ("null", "null")
    parts = s.split("-")
    if len(parts) == 2:
        friction, side = parts
    else:
        # fallback for malformed entries
        friction, side = "null", "null"
    return (SIDE_MAP[side.strip()], FRICTION_MAP[friction.strip()])

# Apply the function to generate the Link
links = []
for _, row in ps2link_df.iterrows():
    side1, friction1 = parse_scenario(row["Scenario 1 [TKT]"])
    side2, friction2 = parse_scenario(row["Scenario 2 [VB]"])
    side3, friction3 = parse_scenario(row["Scenario 3 [TB]"])
    side4, friction4 = parse_scenario(row["Scenario 4 [VKT]"])
    
    link = BASE_LINK.format(
        side1=side1, friction1=friction1,
        side2=side2, friction2=friction2,
        side3=side3, friction3=friction3,
        side4=side4, friction4=friction4
    )
    links.append(link)

# Assign the generated links back to the DataFrame
ps2link_df["Link"] = links

# Save the updated DataFrame to a new CSV (or overwrite)
ps2link_df.to_csv("Q-maps - PS2Links.csv", index=False)
# ps2link_df.to_csv("Q-maps - PS2Links.tsv", index=False, sep='\t')
