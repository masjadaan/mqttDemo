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
    client.on_message = get_location

    try:
        logging.info(f"Establishing connection to Broker: {BROKER['IP']}")
        client.connect(BROKER['IP'], BROKER['PORT'], BROKER['KEEPALIVE'])
        client.loop_start()
        logging.info("Connected to broker.")
    except Exception as e:
        logging.error(f"Failed to connect to broker: {e}")
        sys.exit(1)

    return client


def subscribe_location(client, topic, qos=0):
    try:
        client.subscribe(topic=topic,
                         qos=qos)
        logging.info(f"Subscribed to topic: {topic}")
    except Exception as e:
        logging.error(f"Error subscribing to topic: {e}")


def get_location(client, userdata, message):
    try:
        logging.info(f"Received message: {message.payload.decode()}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")


def signal_handler(sig, frame):
    global running
    logging.info("Signal received, stopping subscriber...")
    running = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client_id = "car_location_subscriber"
    subscriber = init_client(client_name=client_id)

    if wait_for_connection(subscriber):
        subscribe_location(subscriber,
                           topic=CAR_LOCATION_TOPIC,
                           qos=1)
        try:
            while running:
                if not subscriber.is_connected():
                    logging.warning("Lost connection. Reconnecting...")
                    if not wait_for_connection(subscriber):
                        logging.error("Failed to reconnect to the broker.")
                        running = False
                sleep(1)
        except Exception as e:
            logging.error(f"Subscriber encountered an error: {e}")
    else:
        logging.error("Failed to establish connection to the broker.")

    subscriber.loop_stop()
    subscriber.disconnect()
    logging.info("Subscriber stopped.")
