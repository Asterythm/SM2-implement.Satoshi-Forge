from sm2 import *  # Reuse SM2 utilities for simplicity

# secp256k1 parameters for Bitcoin
p_secp = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a_secp = 0
b_secp = 7
Gx_secp = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy_secp = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
n_secp = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G_secp = Point(Gx_secp, Gy_secp)

# Override curve parameters
p = p_secp
a = a_secp
b = b_secp
G = G_secp
n = n_secp

d_fake = random.randint(1, n-1)
PA_fake = scalar_mul(d_fake, G)
message = "I am Satoshi Nakamoto"
r, s = sign(d_fake, message)
print("Forged signature (r,s):", r, s)
print("Message:", message)
print("Fake pubkey (hex):", hex(PA_fake.x), hex(PA_fake.y))

# Hypothetical k leak
k_leaked = random.randint(1, n-1)
r_hyp, s_hyp = sign(d_fake, "Hypothetical message", fixed_k=k_leaked)
e_hyp = sm3_hash("Hypothetical message".encode()) % n
inv = mod_inverse((s_hyp + r_hyp) % n, n)
d_recovered = ((k_leaked - s_hyp) % n * inv) % n
print("Recovered d from k leak:", d_recovered == d_fake)
new_r, new_s = sign(d_recovered, "Forged message")
print("Forged new sig:", new_r, new_s)