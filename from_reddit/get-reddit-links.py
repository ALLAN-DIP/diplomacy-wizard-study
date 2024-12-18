import json

with open('from_reddit.json') as f:
    data = json.load(f)

for post in data:
    print(f"https://www.reddit.com/r/diplomacy/comments/{post['post_id']}")
