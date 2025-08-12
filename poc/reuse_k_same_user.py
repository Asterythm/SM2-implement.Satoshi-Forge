from sm2 import *

d, PA = key_gen()
k_reused = random.randint(1, n-1)
r1, s1 = sign(d, "M1", fixed_k=k_reused)
r2, s2 = sign(d, "M2", fixed_k=k_reused)
num = (s2 - s1) % n
den = (s1 - s2 + r1 - r2) % n
if den == 0:
    print("Denominator zero")
else:
    inv_den = mod_inverse(den, n)
    d_recovered = (num * inv_den) % n
    print("Recovered d:", d_recovered == d)