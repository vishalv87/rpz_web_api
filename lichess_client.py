import berserk

token = ""

session = berserk.TokenSession(token)
client = berserk.Client(session)

result = client.account.get()
print(result)
