from kafka import KafkaProducer, KafkaConsumer
import json
from core.config import settings

class EventService:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER)

    def publish_onboarding_event(self, user_id: str, role: str):
        event = json.dumps({'type': 'new_user', 'user_id': user_id, 'role': role})
        self.producer.send('onboarding-events', event.encode('utf-8'))
