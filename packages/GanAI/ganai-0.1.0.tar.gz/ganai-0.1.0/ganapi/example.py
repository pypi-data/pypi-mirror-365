

from ganapi.client import GanAI

client = GanAI(api_key="TOSMi-eVM5anzNuSE84xv7FkWHim06CCAqWgS9qP")
print(client.ping())

# client.sound_effect(prompt="rain dropping on glass", creativity=0.7, duration=10, num_variants=4)
# print(client.account_details())
# print(client.get_credit_info())
