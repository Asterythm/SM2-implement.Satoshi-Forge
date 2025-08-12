from sm2 import *

def ecdsa_sign(d, M, fixed_k=None):
    e = sm3_hash(M.encode()) % n
    k = fixed_k if fixed_k else random.randint(1, n-1)
    R = scalar_mul(k, G)
    r = R.x % n
    inv_k = mod_inverse(k, n)
    s = (inv_k * (e + r * d % n)) % n
    return r, s

d = random.randint(1, n-1)
M = "Test"
k_shared = random.randint(1, n-1)
r1, s1 = ecdsa_sign(d, M, fixed_k=k_shared)
r2, s2 = sign(d, M, fixed_k=k_shared)
e1 = sm3_hash(M.encode()) % n
num = (s1 * s2 - e1) % n
den = (r1 - s1 * s2 - s1 * r2) % n
inv = mod_inverse(den, n)
d_recovered = (num * inv) % n
print("Recovered d:", d_recovered == d)