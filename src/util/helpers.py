from typing import Union
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def is_valid_uuid(value) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
    except AttributeError:
        return False


def is_int(number: Union[int, float]) -> bool:
    # Check if it is integer and convert numpy.bool_ to bool by bool()
    try:
        return bool((number - int(number) == 0))
    except ValueError:
        return False
    except TypeError:
        return False
