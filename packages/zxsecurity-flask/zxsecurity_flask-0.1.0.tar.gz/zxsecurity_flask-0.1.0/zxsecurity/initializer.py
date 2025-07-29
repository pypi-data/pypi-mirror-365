from fastapi import requests
import zxsecurity
import zxsecurity.modules
import zxsecurity.modules.utils
from .modules import executor
from .modules import scanner
import time
import threading
import logging

def launch(params: dict):
    if not isinstance(params, dict):
        raise TypeError("Expected a dictionary as input.")

    required_fields = {
        "db_module": dict,
        "cl_logs": bool,
        "request_limit": dict,
        "port": int,
        "upload_files": dict,
    }

    for key, expected_type in required_fields.items():
        value = params.get(key)
        if value is None:
            raise ValueError(f"Missing required key: '{key}'")
        if not isinstance(value, expected_type):
            raise ValueError(f'"{key}" must be of type {expected_type.__name__}, but got {type(value).__name__}')

    db_module = params["db_module"]
    req_limit = params["request_limit"]
    upload_files = params["upload_files"]

    db_fields = {
        "enabled": bool,
        "db_folder": str,
    }

    req = {
        "request": int,
        "milliseconds": int,
    }

    upload_files_schema = {
        "allowed_extensions": list,
        "max_size_mb": float,
        "max_size_per_file": float,
    }

    for key, expected_type in db_fields.items():
        value = db_module.get(key)
        if value is None:
            raise ValueError(f"Missing key in 'db_module': '{key}'")
        if not isinstance(value, expected_type):
            raise ValueError(f"'db_module.{key}' must be of type {expected_type.__name__}, but got {type(value).__name__}")

    for key, expected_type in req.items():
        value = req_limit.get(key)
        if value is None:
            raise ValueError(f"Missing key in 'request_limit': '{key}'")
        if not isinstance(value, expected_type):
            raise ValueError(f"'request_limit.{key}' must be of type {expected_type.__name__}, but got {type(value).__name__}")

    for key, expected_type in upload_files_schema.items():
        value = upload_files.get(key)
        if value is None:
            raise ValueError(f"Missing key in 'upload_files': '{key}'")
        if not isinstance(value, expected_type):
            raise ValueError(f"'upload_files.{key}' must be of type {expected_type.__name__}, but got {type(value).__name__}")

    unexpected_keys = set(params.keys()) - set(required_fields.keys())
    if unexpected_keys:
        raise ValueError(f"Unexpected keys in 'params': {unexpected_keys}")

    unexpected_db = set(db_module.keys()) - set(db_fields.keys())
    if unexpected_db:
        raise ValueError(f"Unexpected keys in 'db_module': {unexpected_db}")

    unexpected_req = set(req_limit.keys()) - set(req.keys())
    if unexpected_req:
        raise ValueError(f"Unexpected keys in 'request_limit': {unexpected_req}")

    unexpected_upload_files = set(upload_files.keys()) - set(upload_files_schema.keys())
    if unexpected_upload_files:
        raise ValueError(f"Unexpected keys in 'upload_files': {unexpected_upload_files}")

    if not executor.isExists("keys.json"):
        keys_data = {
            "auth": executor.generate_token(16),
            "encryption_key": executor.generate_token(32),
        }
        executor.create_json("keys.json", "security", keys_data)

    """
    if not executor.isExistsSecurity("restricted.json"):
        restricted_data = {}
        executor.create_folder_security("restricted")
        executor.create_json_security("restricted.json", restricted_data)
    """

    executor.create_folder("security")
    executor.create_json("data.json", "security", params)
    executor.create_json("flood_log.json", "security", {})

    if not executor.load_json_data("cl_logs"):
        log_flask = logging.getLogger('werkzeug')
        log_flask.setLevel(logging.ERROR)

    print("\033[38;2;128;0;0m\033[1m[ZXsecurity]\033[0m ZXsecurity launched successfully and is operational.")

    try:
        while True:
            scanner.scan()
            time.sleep(1)
    except KeyboardInterrupt:
        if executor.load_json_data("cl_logs"):
            print("\n\033[38;2;128;0;0m\033[1m[ZXsecurity]\033[0m Shutdown requested by user. Exiting gracefully.\033[0m")