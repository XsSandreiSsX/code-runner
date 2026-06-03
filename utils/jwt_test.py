"""
This file does not contain any secret keys, all data is test and randomly generated.
"""

from utils.jwt_generator import generate_internal_jwt


token = generate_internal_jwt("stepik", jwt_secret="1989f60b2285a8f19a5b021cd0fe19dd46e8da4db1b711ee1e583ffa0030811f", ttl=10214124)
token2 = generate_internal_jwt("service2", jwt_secret="aea52cdbea3ec5caf53df415698f1a0407c0e13e8847111d078895d960a1ec8c", ttl=15000)

print(token)
print(token2)