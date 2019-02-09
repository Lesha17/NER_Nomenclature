# -*- coding: utf-8 -*-

learn = []
test = []
pool = []

with open("first_pool_learn.tsv") as lf:
    for line in lf:
    	learn.append(line.replace("\n", ""))

print("Learn: ", learn[1:10])

with open("first_pool_validate.tsv") as tf:
    for line in tf:
    	test.append(line.replace("\n", ""))

print("Test: ", test[1:10])

with open("first_pool.tsv") as f:
    for line in f:
    	pool.append(line.replace("\n", ""))

print("Pool: ", pool[1:10])

print("Pool length: " + str(len(pool)))

print([l for l in pool if (any(lt.startswith(l) for lt in test) or any(ll.startswith(l) for ll in learn))])

pool_filtered = [l + "\n" for l in pool if not (any(lt.startswith(l) for lt in test) or any(ll.startswith(l) for ll in learn))]

print("Filtered pool length: " + str(len(pool_filtered)))

with open("first_pool_filtered.tsv", "w") as result:
    result.writelines(pool_filtered)