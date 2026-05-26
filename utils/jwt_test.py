from utils.jwt_generator import generate_internal_jwt


token = generate_internal_jwt("stepik", jwt_secret="d6ab8156244eee245a3089bfa4efe4536682f4821202117148d84b5caf327297", ttl=15000)
token2 = generate_internal_jwt("codeforces", jwt_secret="29fc1f548a6f667fe1446102ae0bf1acd640488b26d37bf147007f09756892c1", ttl=15000)

print(token)
print(token2)