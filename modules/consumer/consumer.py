import os
from kafka import KafkaConsumer
import psycopg2
import json

TOPIC_NAME = 'items'
KAFKA_SERVER = os.environ["KAFKA_HOST"] + ':' + os.environ["KAFKA_PORT"]
consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER)
for message in consumer:
    location_str = message.value.decode("utf-8").replace("'", "\"")
    location_json = json.loads(location_str)
    # {'longitude': '22.55363', 'person_id': 2, 'latitude': '-22.290883', 'creation_time': '2020-08-15T10:37:06'}
    person_id = location_json['person_id']
    latitude = location_json['latitude']
    longitude = location_json['longitude']
    creation_time = location_json['creation_time']
    data = str(person_id) + " " + latitude + " " + longitude  + " " + creation_time
    print(data)

    conn = psycopg2.connect(database=os.environ["DB_NAME"],
                            host=os.environ["DB_HOST"],
                            user=os.environ["DB_USERNAME"],
                            password=os.environ["DB_PASSWORD"],
                            port=os.environ["DB_PORT"])
    cursor = conn.cursor()
    postgres_insert_query = """ insert into location (person_id, coordinate, creation_time)
        values (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
    """
    record_to_insert = (person_id, longitude, latitude, creation_time)
    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()
