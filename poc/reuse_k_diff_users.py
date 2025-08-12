from sm2 import *

dA, PA = key_gen()
dB, PB = key_gen()
k_reused = random.randint(1, n-1)
r1, s1 = sign(dA, "M1", fixed_k=k_reused)
r2, s2 = sign(dB, "M2", fixed_k=k_reused)
num = (k_reused - s2) % n
den = (s2 + r2) % n
inv = mod_inverse(den, n)
dB_recovered = (num * inv) % n
print("Alice recovered dB:", dB_recovered == dB)