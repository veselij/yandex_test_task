import random as r


N = 10000

print('''{"data":[''')
for i in range(1, N):
    w = r.randint(1, 10)
    reg = r.randint(1,10)
    h = []
    s1 = r.randint(8, 12)
    e1 = r.randint(15, 17)
    s2 = r.randint(17, 19)
    e2 = r.randint(21, 23)
    h.append(f'''"{s1}:00-{e1}:00", "{s2}:00-{e2}:00"''')
    row = f'''{{"order_id": {i}, "weight": {w}, "region": {reg}, "delivery_hours": [{",".join(h)}]}},'''
    if i == N-1:
        print(row[:-1])
    else:
        print(row)

print(''']}''')
