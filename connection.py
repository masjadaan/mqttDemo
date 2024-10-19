import logging
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)

BROKER = {
    'IP': "192.168.178.20",
    'PORT': 1883,
    'KEEPALIVE': 3
}


class MqttReturnCode(Enum):
    SUCCESSFUL_CONNECTION = 0
    INCORRECT_PROTOCOL_VERSION = 1
    INVALID_CLIENT_IDENTIFIER = 2
    SERVER_UNAVAILABLE = 3
    BAD_USERNAME_OR_PASSWORD = 4
    NOT_AUTHORIZED = 5

    def __str__(self):
        descriptions = {
            MqttReturnCode.SUCCESSFUL_CONNECTION: "Connection successful",
            MqttReturnCode.INCORRECT_PROTOCOL_VERSION: "Connection refused - incorrect protocol version",
            MqttReturnCode.INVALID_CLIENT_IDENTIFIER: "Connection refused - invalid client identifier",
            MqttReturnCode.SERVER_UNAVAILABLE: "Connection refused - server unavailable",
            MqttReturnCode.BAD_USERNAME_OR_PASSWORD: "Connection refused - bad username or password",
            MqttReturnCode.NOT_AUTHORIZED: "Connection refused - not authorized",
        }
        return descriptions.get(self, "Unknown error")


def on_connect(client, userdata, connect_flags, rc):
    try:
        rc_code = MqttReturnCode(rc)
        if rc_code == MqttReturnCode.SUCCESSFUL_CONNECTION:
            logging.info(f"Connected successfully, returned code: {rc} ({rc_code})")
        else:
            logging.error(f"Connection failed, returned code: {rc} ({rc_code})")
    except ValueError:
        logging.error(f"Connection failed, unknown return code: {rc}")


def on_disconnect(client, userdata, rc):
    rc_code = MqttReturnCode(rc)
    if rc_code == MqttReturnCode.SUCCESSFUL_CONNECTION:
        logging.warning("Unexpected disconnection from MQTT broker.")
    else:
        logging.info(f"Client disconnected from broker with code: {rc_code}")


def wait_for_connection(client, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if client.is_connected():
            logging.info("Client connected successfully.")
            return True
        logging.info("Waiting for connection...")
        time.sleep(1)
    logging.error("Connection timeout.")
    return False
