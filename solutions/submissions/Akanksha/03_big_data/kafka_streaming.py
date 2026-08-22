"""
Presight — Task 3.2: Kafka Streaming Pipeline
Author: Akanksha Shreya

Simulator → [Kafka Topic: presight.project.events] → Consumer → outputs/kafka/
                                          |
                                          +--> [Kafka Topic: presight.escalations.critical] (Critical severity only)
"""

import json
import os
import time
import argparse
import logging
import glob
from datetime import datetime

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
EVENTS_DIR = os.path.join(BASE_DIR, "datasets", "events_stream")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "kafka")

KAFKA_BOOTSTRAP    = "localhost:9092"
TOPIC_EVENTS       = "presight.project.events"
TOPIC_ESCALATIONS  = "presight.escalations.critical"


# ---------------------------------------------------------------------------
# Topic management
# ---------------------------------------------------------------------------
def create_topics():
    """
    Create the required Kafka topics if they don't already exist.
    """
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP)

    topics = [
        NewTopic(name=TOPIC_EVENTS, num_partitions=3, replication_factor=1),
        NewTopic(name=TOPIC_ESCALATIONS, num_partitions=1, replication_factor=1),
    ]

    try:
        result = admin.create_topics(new_topics=topics, validate_only=False)
        logger.info(f"Topic creation result: {result}")
    except TopicAlreadyExistsError:
        logger.info("Topics already exist, skipping creation")
    finally:
        admin.close()

    # Verify creation actually landed (Kafka metadata propagation can lag
    # slightly right after creation, so we check rather than assume).
    time.sleep(1)
    check_admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP)
    existing = check_admin.list_topics()
    check_admin.close()
    for t in [TOPIC_EVENTS, TOPIC_ESCALATIONS]:
        status = "confirmed" if t in existing else "NOT FOUND"
        logger.info(f"Topic '{t}': {status}")


# ---------------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------------
def build_producer():
    """
    Create and return a KafkaProducer configured to serialize messages as JSON.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
        retries=3,
    )
    return producer


def run_producer(events_dir: str):
    """
    Read events from the JSONL files and publish them to Kafka.
    All events go to TOPIC_EVENTS. Events with event_type ==
    'escalation_raised' AND payload.severity == 'Critical' also get
    published to TOPIC_ESCALATIONS (severity-based routing).
    """
    producer = build_producer()

    total_sent = 0
    critical_escalations_sent = 0

    file_list = sorted(glob.glob(os.path.join(events_dir, "events_*.jsonl")))
    logger.info(f"Producing events from {len(file_list)} files")

    for filepath in file_list:
        with open(filepath, "r") as f:
            for line in f:
                event = json.loads(line)
                key = event.get("project_id") or event.get("user_id") or event.get("event_id")

                producer.send(TOPIC_EVENTS, key=key, value=event)
                total_sent += 1

                if (event.get("event_type") == "escalation_raised"
                        and event.get("payload", {}).get("severity") == "Critical"):
                    producer.send(TOPIC_ESCALATIONS, key=key, value=event)
                    critical_escalations_sent += 1

                if total_sent % 10000 == 0:
                    logger.info(f"Sent {total_sent} events so far...")

    producer.flush()
    producer.close()

    logger.info(f"Producer complete. Total events sent: {total_sent}")
    logger.info(f"Critical escalations routed to {TOPIC_ESCALATIONS}: {critical_escalations_sent}")


# ---------------------------------------------------------------------------
# Consumer
# ---------------------------------------------------------------------------
def build_consumer(topic: str, group_id: str):
    """
    Create and return a KafkaConsumer for the given topic.
    """
    # YOUR CODE HERE
    return None


def run_consumer(topic: str, group_id: str, output_path: str):
    """
    Consume events from the given topic and write a summary to output_path.
    """
    # YOUR CODE HERE
    pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["produce", "consume", "topics"], required=True)
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.mode == "topics":
        create_topics()
    elif args.mode == "produce":
        create_topics()
        run_producer(EVENTS_DIR)
    elif args.mode == "consume":
        run_consumer(TOPIC_EVENTS, "presight-consumer-group", os.path.join(OUTPUT_DIR, "summary.json"))