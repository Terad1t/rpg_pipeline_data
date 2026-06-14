from faker import Faker
import json
import os

fk = Faker("en_US")
users = []
file = "data/"
path_file = os.path.join(file, "dados.json")


def generate_users(num_users):
    users = []
    for i in range(num_users):

        user = {
            "id": i + 6,
            "name": fk.name(),
            "email": fk.email(),
            "device_id": fk.uuid4(),
        }

        users.append(user)
    
    return users

with open(path_file, "w", encoding="utf-8") as f:
    json.dump(generate_users(100), f, indent=4, ensure_ascii=False)