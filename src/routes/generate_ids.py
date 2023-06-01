import uuid


def generate_driver_id():
    return "D" + str(uuid.uuid4())


def generate_passenger_id():
    return "P" + str(uuid.uuid4())
