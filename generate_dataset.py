import json, random
from pathlib import Path

random.seed(42)

traits = [5, 1, 3, 4, 5, 5, 2, 4, 4, 5]  # 不活跃但能力强

# action ids by enum order
A = list(range(0, 4))
B = list(range(4, 7))
C = list(range(7, 10))
D = list(range(10, 31))
E = list(range(31, 58))

# desc id ranges by group/sub-group according to enum order
Q = {
    'Q1A': (0, 3), 'Q1B': (4, 7), 'Q1C': (8, 11),
    'Q2A': (12, 15), 'Q2B': (16, 18), 'Q2C': (19, 22), 'Q2D': (23, 25), 'Q2E': (26, 29),
    'Q3A': (30, 33), 'Q3B': (34, 37), 'Q3C': (38, 41), 'Q3D': (42, 45),
    'Q4A': (46, 48), 'Q4B': (49, 51), 'Q4C': (52, 54), 'Q4D': (55, 57),
    'Q5A': (58, 62), 'Q5B': (63, 66), 'Q5C': (67, 70), 'Q5D': (71, 74),
    'Q6A': (75, 78), 'Q6B': (79, 82), 'Q6C': (83, 86), 'Q6D': (87, 90),
    'Q7A': (91, 93), 'Q7B': (94, 97), 'Q7C': (98, 100), 'Q7D': (101, 103), 'Q7E': (104, 108), 'Q7F': (109, 112)
}

def pick(r):
    return random.randint(*Q[r])

def desc_for_action(aid):
    # A: Q2-A, Q2-C, Q3, Q4
    if aid in A:
        return [pick('Q2A'), pick('Q2C'), pick('Q3A'), pick('Q3B'), pick('Q3C'), pick('Q3D'), pick('Q4A'), pick('Q4B'), pick('Q4C'), pick('Q4D')]
    # B: Q2-A, Q2-B, Q2-C
    if aid in B:
        return [pick('Q2A'), pick('Q2B'), pick('Q2C')]
    # C: Q2, Q3
    if aid in C:
        return [pick('Q2A'), pick('Q2B'), pick('Q2C'), pick('Q2D'), pick('Q2E'), pick('Q3A'), pick('Q3B'), pick('Q3C'), pick('Q3D')]
    # D: Q1, Q2, Q4, Q5, Q6, Q7
    if aid in D:
        return [pick('Q1A'), pick('Q1B'), pick('Q1C'), pick('Q2A'), pick('Q2B'), pick('Q2C'), pick('Q2D'), pick('Q2E'), pick('Q4A'), pick('Q4B'), pick('Q4C'), pick('Q4D'), pick('Q5A'), pick('Q5B'), pick('Q5C'), pick('Q5D'), pick('Q6A'), pick('Q6B'), pick('Q6C'), pick('Q6D'), pick('Q7A'), pick('Q7B'), pick('Q7C'), pick('Q7D'), pick('Q7E'), pick('Q7F')]
    # E: Q1,Q2,Q3
    return [pick('Q1A'), pick('Q1B'), pick('Q1C'), pick('Q2A'), pick('Q2B'), pick('Q2C'), pick('Q2D'), pick('Q2E'), pick('Q3A'), pick('Q3B'), pick('Q3C'), pick('Q3D')]

teacher_texts = [
    "请先独立思考三十秒，再告诉我你的判断。",
    "这一步谁愿意补充一下理由？",
    "先把关键公式写下来，不要急着报答案。",
    "看黑板第三行，注意单位有没有统一。",
    "你先读题干，其他同学先不要提示。",
    "这个地方可以有不同做法，说说你的思路。",
    "我们按步骤来，先完成第一问。",
    "请把你的结论再说完整一点。",
    "先和同桌确认一下，再举手回答。",
    "如果不确定，可以先写草稿再发言。",
]
student_texts = [
    "老师，我想先确认一下题目条件。",
    "我觉得这里应该先化简，再代入。",
    "我还没想好，能再给我一点时间吗？",
    "我先把过程写完，再回答。",
    "这个结论我有把握，但是步骤还差一点。",
    "我同意他的方法，不过结果要再检查。",
    "我可以补充一个更快的做法。",
    "我有点犹豫，可能这里符号写反了。",
    "我先读一遍材料，再给出答案。",
    "我想用图示解释这个关系。",
]

# logic templates
prev_next_rules = {
    7: {'prev': [4], 'next': [8]},  # RaiseHand often after looking target and then lower
    8: {'prev': [7], 'next': []},
    20: {'prev': [10], 'next': [31]}, # speak answer then write answer
    31: {'prev': [20], 'next': []},
    35: {'prev': [4], 'next': []}, # write copy needs lookAt
    41: {'prev': [4], 'next': []},
    39: {'prev': [31], 'next': []},
}

def sample_actions(pool, max_count=2):
    k = 1 if random.random() < 0.82 else max_count
    return random.sample(pool, k)

def make_record(pool):
    current = sample_actions(pool)
    prev, nxt = [], []
    for aid in current:
        if aid in prev_next_rules and random.random() < 0.6:
            prev.extend(prev_next_rules[aid]['prev'])
            nxt.extend(prev_next_rules[aid]['next'])
    prev = sorted(set(prev))
    nxt = sorted(set(nxt))

    speaker = 'Teacher' if random.random() < 0.45 else 'Student'
    text = random.choice(teacher_texts if speaker == 'Teacher' else student_texts)

    action_desc = [{'action_id': a, 'desc_ids': desc_for_action(a)} for a in current]
    next_action_desc = [{'action_id': a, 'desc_ids': desc_for_action(a)} for a in nxt]

    return {
        'traits': traits,
        'prev_action_ids': prev,
        'current_action_ids': current,
        'next_action_ids': nxt,
        'text': text,
        'speaker': speaker,
        'action_desc': action_desc,
        'next_action_desc': next_action_desc,
    }

outdir = Path('data')
outdir.mkdir(exist_ok=True)

splits = {
    'train_A_posture.jsonl': A,
    'train_B_attention.jsonl': B,
    'train_C_gesture.jsonl': C,
    'train_D_vocal.jsonl': D,
    'train_E_task.jsonl': E,
}

all_records = []
for fn, pool in splits.items():
    records = [make_record(pool) for _ in range(500)]
    all_records.extend(records)
    with (outdir / fn).open('w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

# dev set sampled from all training
random.shuffle(all_records)
dev = all_records[:300]
with (outdir / 'dev.jsonl').open('w', encoding='utf-8') as f:
    for r in dev:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('generated', len(all_records), 'train and', len(dev), 'dev')
