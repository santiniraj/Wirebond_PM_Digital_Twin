# src/machine_config.py

MACHINE_MAP = {
    0: "WBO001 - Wire Bond Unit 01",
    1: "WBO002 - Wire Bond Unit 02",
    2: "WBO003 - Wire Bond Unit 03"
}

VALID_MACHINES = list(MACHINE_MAP.values())


def get_machine_name(type_id):
    return MACHINE_MAP.get(type_id, "UNKNOWN")