import random as r


couriers = ["foot", "bike", "car"]
N = 100

print('''{"data":[''')
for i in range(1, N):
    c = couriers[r.randint(0,2)]
    reg = []
    for j in range(r.randint(1,4)):
        rr = r.randint(1, 10)
        reg.append(rr) if rr not in reg else reg
    h = []
    s1 = r.randint(8, 12)
    e1 = r.randint(15, 17)
    s2 = r.randint(17, 19)
    e2 = r.randint(21, 23)
    h.append(f'''"{s1}:00-{e1}:00", "{s2}:00-{e2}:00"''')
    row = f'''{{"courier_id": {i}, "courier_type": "{c}", "regions": {reg}, "working_hours": [{",".join(h)}]}},'''
    if i == N-1:
        print(row[:-1])
    else:
        print(row)

print(''']}''')
