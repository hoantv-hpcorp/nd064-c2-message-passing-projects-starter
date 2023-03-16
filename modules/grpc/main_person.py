import time
import os
from concurrent import futures

import grpc
import psycopg2

import person_pb2
import person_pb2_grpc

class PersonServicer(person_pb2_grpc.PersonServiceServicer):
    def Get(self, request, context):
        conn = psycopg2.connect(database=os.environ["DB_NAME"],
                                host=os.environ["DB_HOST"],
                                user=os.environ["DB_USERNAME"],
                                password=os.environ["DB_PASSWORD"],
                                port=os.environ["DB_PORT"])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM person")
        personAll = cursor.fetchall()
        persons = []
        for person in personAll:
            personMessage = person_pb2.PersonMessage()
            personMessage.id=person[0]
            personMessage.first_name=person[1]
            personMessage.last_name=person[2]
            personMessage.company_name=person[3]
            persons.append(personMessage)

        result = person_pb2.PersonMessageList()
        result.persons.extend(persons)
        return result

# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServicer(), server)


print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
