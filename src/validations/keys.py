from typing import TypedDict
from src.config import ENVIRONMENT_VARIABLES
import src.services.logservice as log


class Validations(TypedDict):
    Succeed: bool
    MissingConfigurations: list


validation_status: Validations = {"Succeed": False, "MissingConfigurations": []}


def _pairing_key_value(test_dict: dict) -> list:
    """Check and return if the value of the key existed

    Args:
        test_dict (dict): A dictionary needs to validated.

    Returns:
        list: return the keys missing value with list.
    """
    keys_missing_value = []
    for key, val in test_dict.items():
        if val is None or val == "":
            keys_missing_value.append(key)
            log.error(f"The key: {key} has no value")
            validation_status["Succeed"] = False
        else:
            log.info(f"The key: {key} has value.")
            validation_status["Succeed"] = True

    return keys_missing_value


def check() -> Validations:
    """Check and return validation status"""
    # TODO: the format of the response need to update once the API design ready
    validation_status["MissingConfigurations"] = _pairing_key_value(
        ENVIRONMENT_VARIABLES
    )
    return validation_status
