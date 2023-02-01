import logging
import os
from src.config import ENVIRONMENT_VARIABLES


def info(message: str, properties=None):
    current_filename = os.path.basename(__file__)
    if properties is None:
        # TODO: optimize the properties
        properties = {
            "custom_dimensions": {
                "fileName": current_filename,
            }
        }
    logging.info(message, extra=properties)


def warning(message: str, properties=None):
    current_filename = os.path.basename(__file__)
    if properties is None:
        properties = {
            "custom_dimensions": {
                "fileName": current_filename,
            }
        }
    logging.warning(message, extra=properties)


def error(message: str, properties=None):
    current_filename = os.path.basename(__file__)
    if properties is None:
        properties = {
            "custom_dimensions": {
                "fileName": current_filename,
            }
        }
    logging.error(message, extra=properties)


def debug(message: str, properties=None):
    current_filename = os.path.basename(__file__)
    if properties is None:
        properties = {
            "custom_dimensions": {
                "fileName": current_filename,
            }
        }
    logging.debug(message, extra=properties)


def get_custom_properties(
    module_name: str = None,
    current_filename: str = None,
    run_id: str = None,
):
    custom_dimensions = {}
    if current_filename is None:
        current_filename = os.path.basename(__file__)
    custom_dimensions["fileName"] = current_filename

    if module_name is not None:
        custom_dimensions["moduleName"] = module_name

    if run_id is not None:
        custom_dimensions["runId"] = run_id

    properties = {"custom_dimensions": custom_dimensions}
    return properties
