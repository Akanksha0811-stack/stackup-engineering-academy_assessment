import json

count = 0
for line in open('datasets/events_stream/events_2025_01.jsonl'):
    e = json.loads(line)
    if e['event_type'] in ('escalation_raised', 'escalation_resolved'):
        print(e)
        count += 1
        if count >= 6:
            break