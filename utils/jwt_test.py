"""
This file does not contain any secret keys, all data is test and randomly generated.
"""

from utils.jwt_generator import generate_internal_jwt


token = generate_internal_jwt("service1", jwt_secret="31415a8ff2c88ad6ab50b770f993de78e6fc1f1106662625311cd1b61444ea44", ttl=10214124)
token2 = generate_internal_jwt("service2", jwt_secret="aea52cdbea3ec5caf53df415698f1a0407c0e13e8847111d078895d960a1ec8c", ttl=15000)

print(token)
print(token2)