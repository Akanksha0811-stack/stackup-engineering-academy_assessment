"""
Presight — Task 3.2: Kafka Streaming Pipeline
Author: Akanksha Shreya
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

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
EVENTS_DIR = os.path.join(BASE_DIR, "datasets", "events_stream")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "kafka")

KAFKA_BOOTSTRAP    = "localhost:9092"
TOPIC_EVENTS       = "presight.project.events"
TOPIC_ESCALATIONS  = "presight.escalations.critical"


def create_topics():
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

    time.sleep(1)
    check_admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP)
    existing = check_admin.list_topics()
    check_admin.close()
    for t in [TOPIC_EVENTS, TOPIC_ESCALATIONS]:
        status = "confirmed" if t in existing else "NOT FOUND"
        logger.info(f"Topic '{t}': {status}")


def build_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
        retries=3,
    )
    return producer


def run_producer(events_dir: str):
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


def build_consumer(topic: str, group_id: str):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=10000,
    )
    return consumer


def run_consumer(topic: str, group_id: str, output_path: str):
    consumer = build_consumer(topic, group_id)
    total_consumed = 0
    event_type_counts = {}
    project_ids_seen = set()

    logger.info(f"Starting consumer on topic: {topic}")

    for message in consumer:
        event = message.value
        total_consumed += 1
        event_type = event.get("event_type", "unknown")
        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        if event.get("project_id"):
            project_ids_seen.add(event["project_id"])
        if total_consumed % 10000 == 0:
            logger.info(f"Consumed {total_consumed} events so far...")

    consumer.close()

    summary = {
        "topic": topic,
        "total_consumed": total_consumed,
        "unique_projects_seen": len(project_ids_seen),
        "event_type_breakdown": event_type_counts,
        "consumed_at": datetime.now().isoformat(),
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Consumer complete. Total events consumed: {total_consumed}")
    logger.info(f"Summary written to: {output_path}")

    return summary


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
