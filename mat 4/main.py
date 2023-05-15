import numpy as np
import matplotlib.pyplot as plt
import random
import tabulate

print()

a0 = 3
a1 = 2
a2 = 1


def f(x):
    return a0 * (a1 ** x) * (a2 ** (x ** 2))


gn = [30, 20, 16, 26, 28]
xs = [
    6.8,
    7.84,
    8.88,
    9.92,
    10.96,
    12,
]
fs = [
    float(f(6.8)),
    float(f(7.84)),
    float(f(8.88)),
    float(f(9.92)),
    float(f(10.96)),
    float(f(12)),
]

res = []

for i, n in enumerate(gn):
    ar, br = fs[i:i+2]
    ax, bx = xs[i:i+2]
    for j in range(n):
        res.append((random.uniform(ax, bx),
                   random.uniform(ar, br) + random.random()))

res.sort()

X = [r[0] for r in res]
Y = [r[1] for r in res]
table = []

for i in range(len(X)):
    table.append((i, X[i], Y[i]))

print(tabulate.tabulate(table))
# print(fs)
plt.plot(X, Y, 'ro')

plt.show()
