from sm2 import *

d, PA = key_gen()
M = "Test"
k_leaked = random.randint(1, n-1)
r, s = sign(d, M, fixed_k=k_leaked)
ZA = compute_ZA('user@example.com', PA)
e = sm3_hash(int_to_bytes(ZA) + M.encode()) % n
x1 = scalar_mul(k_leaked, G).x % n
if (e + x1) % n != r:
    print("Invalid k")
else:
    inv = mod_inverse((s + r) % n, n)
    d_recovered = ((k_leaked - s) % n * inv) % n
    print("Recovered d:", d_recovered == d)