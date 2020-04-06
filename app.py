import connexion
from connexion import NoContent
from pykafka import KafkaClient
import pykafka
import yaml
import json
import datetime
from flask_cors import CORS, cross_origin
import logging.config
import logging

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

def get_event(offset):
    with open ('kafka_config.yaml', 'r') as f:
        kafka = yaml.safe_load(f.read())

    client = KafkaClient(hosts='{0}:{1}'.format(kafka['kafka']['kafka-server'], kafka['kafka']['kafka-port']))
    topic = client.topics['{0}'.format(kafka['kafka']['topic'])]
    consumer = topic.get_simple_consumer(
        consumer_group="mygroup",
        auto_offset_reset=pykafka.common.OffsetType.EARLIEST,
        reset_offset_on_start=True
    )
    
    consumer.consume()
    consumer.commit_offsets()

    counter = 0
    for message in consumer:
        msg = json.loads(message.value.decode('utf-8', errors='replace'))
        try:
            if offset -1 <= 0:
                logger.info(msg)
                return msg
            if counter == offset -1:
                logger.info(msg)
                return msg
            if counter <= offset -1:
                if msg['type'] == 'Info':
                    counter += 1
                
        except 'KeyError paramater not a number' as KeyError:
            logger.error(KeyError)
            return 404

def get_oldest_event():
    with open ('kafka_config.yaml', 'r') as f:
        kafka = yaml.safe_load(f.read())

    client = KafkaClient(hosts='{0}:{1}'.format(kafka['kafka']['kafka-server'], kafka['kafka']['kafka-port']))
    topic = client.topics['{0}'.format(kafka['kafka']['topic'])]
    consumer = topic.get_simple_consumer(
        consumer_group="mygroup",
        auto_offset_reset=pykafka.common.OffsetType.LATEST -1,
        reset_offset_on_start=True
    )
    consumer.consume()
    consumer.commit_offsets()
    for message in consumer:
        msg = json.loads(message.value.decode('utf-8', errors='replace'))
        return msg


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8110)