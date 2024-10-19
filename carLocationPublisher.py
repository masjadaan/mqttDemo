#!/usr/bin/env python3

import signal
import sys
from time import sleep
import paho.mqtt.client as mqtt
from connection import *
from topics import CAR_LOCATION_TOPIC
import uuid

# Global variable to manage running state
running = True


def init_client(client_name):
    client = mqtt.Client(client_id=f"{client_name}_{uuid.uuid4()}",
                         clean_session=False)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        logging.info(f"Connecting to Broker at {BROKER['IP']}...")
        client.connect(BROKER['IP'], BROKER['PORT'], BROKER['KEEPALIVE'])
        client.loop_start()
        logging.info("Connected to broker.")
    except Exception as e:
        logging.error(f"Failed to connect to broker: {e}")
        sys.exit(1)

    return client


def publish_location(client, payload):
    try:
        result = client.publish(topic=CAR_LOCATION_TOPIC,
                                payload=payload,
                                qos=1,
                                retain=False)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info("Message sent successfully.")
        else:
            logging.error(f"Failed to send message with result code: {result.rc}")
    except Exception as e:
        logging.error(f"Error while publishing: {e}")


def get_gps_coordinates():
    return "The car location is: XYZ"


def signal_handler(sig, frame):
    global running
    logging.info("Signal received, stopping publisher...")
    running = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client_id = "car_location_publisher"
    publisher = init_client(client_name=client_id)

    if wait_for_connection(publisher):
        while running:
            if not publisher.is_connected():
                logging.warning("Lost connection. Reconnecting...")
                if not wait_for_connection(publisher):
                    logging.error("Failed to reconnect to the broker.")
                    running = False
                    break
            location = get_gps_coordinates()
            publish_location(publisher, payload=location)
            sleep(2)
    else:
        logging.error("Failed to establish connection to the broker.")

    publisher.loop_stop()
    publisher.disconnect()
    logging.info("Publisher stopped.")
