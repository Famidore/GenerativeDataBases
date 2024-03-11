import random
import enum
from typing import Optional

men = {
    "Jan": 10,
    "Tomasz": 8,
    "Andrzej": 7,
    "Krzysztof": 6,
    "Wojciech": 5,
}

women = {
    "Anna": 10,
    "Maria": 8,
    "Katarzyna": 7,
    "Małgorzata": 6,
    "Agnieszka": 5,
}


class Gender(str, enum.Enum):
    M = "M"
    F = "F"


def name(sex: Optional[Gender] = None):
    if sex == Gender.M:
        return random.choices(men.keys(), men.values())
    elif sex == Gender.F:
        return random.choices(women.keys(), women.values())
    else:
        combined = {**men, **women}
        return random.choices(combined.keys(), combined.values())
