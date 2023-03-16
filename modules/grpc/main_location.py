import time
import os
from concurrent import futures

import grpc
import psycopg2

import location_pb2
import location_pb2_grpc


class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):
        print("Received a message!")

        request_value = {
            "id": request.id,
            "person_id": request.person_id,
            "longitude": request.longitude,
            "latitude": request.latitude,
            "creation_time": request.creation_time,
        }
        print(request_value)

        return location_pb2.LocationMessage(**request_value)
    
    def Get(self, request, context):
        first_location = location_pb2.LocationMessage(
            id="2222",
            person_id="2",
            longitude="22.5536299999999983",
            latitude="-22.2908830000000009",
            creation_time="2020-08-15T10:37:06"
        )

        second_location = location_pb2.LocationMessage(
            id="3333",
            person_id="3",
            longitude="33.5536299999999983",
            latitude="-33.2908830000000009",
            creation_time="2020-08-15T10:37:06"
        )

        result = location_pb2.LocationMessageList()
        result.locations.extend([first_location, second_location])
        return result
    
    def GetDetail(self, request, context):
        location = location_pb2.LocationMessage(
            id=request.id,
            person_id="2",
            longitude="22.5536299999999983",
            latitude="-22.2908830000000009",
            creation_time="2020-08-15T10:37:06"
        )

        conn = psycopg2.connect(database=os.environ["DB_NAME"],
                                host=os.environ["DB_HOST"],
                                user=os.environ["DB_USERNAME"],
                                password=os.environ["DB_PASSWORD"],
                                port=os.environ["DB_PORT"])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM location WHERE id = " + request.id)
        locationDB = cursor.fetchone()
        print(locationDB)

        return location
    
    def FindByPersonAndDate(self, request, context):
        params = {
            "person_id" : request.person_id,
            "start_date" : request.start_date,
            "end_date" : request.end_date
        }
        conn = psycopg2.connect(database=os.environ["DB_NAME"],
                                host=os.environ["DB_HOST"],
                                user=os.environ["DB_USERNAME"],
                                password=os.environ["DB_PASSWORD"],
                                port=os.environ["DB_PORT"])
        cursor = conn.cursor()
        cursor.execute("""
            select id, person_id, ST_Y(coordinate) as longitude, ST_X(coordinate) as latitude, creation_time
            from "location" l
            where 
                person_id = %(person_id)s
                and creation_time < %(end_date)s
                and creation_time >= %(start_date)s
            """, params)
        locations = cursor.fetchall()
        locationMessages = []
        for location in locations:
            locationMessage = location_pb2.LocationMessage()
            locationMessage.id=location[0]
            locationMessage.person_id=location[1]
            locationMessage.longitude=str(location[2])
            locationMessage.latitude=str(location[3])
            locationMessage.creation_time=str(location[4])
            locationMessages.append(locationMessage)

        result = location_pb2.LocationMessageList()
        result.locations.extend(locationMessages)
        return result

    def FindByDistance(self, request, context):
        params = {
            "person_id" : request.person_id,
            "longitude" : request.longitude,
            "latitude" : request.latitude,
            "meters" : request.meters,
            "start_date" : request.start_date,
            "end_date" : request.end_date
        }
        conn = psycopg2.connect(database=os.environ["DB_NAME"],
                                host=os.environ["DB_HOST"],
                                user=os.environ["DB_USERNAME"],
                                password=os.environ["DB_PASSWORD"],
                                port=os.environ["DB_PORT"])
        cursor = conn.cursor()
        cursor.execute("""
            SELECT  id, person_id, ST_X(coordinate), ST_Y(coordinate), creation_time
            FROM    location
            WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(%(latitude)s,%(longitude)s),4326)::geography, %(meters)s)
            AND     person_id != %(person_id)s
            AND     TO_DATE(%(start_date)s, 'YYYY-MM-DD') <= creation_time
            AND     TO_DATE(%(end_date)s, 'YYYY-MM-DD') > creation_time;
            """, params)
        locations = cursor.fetchall()
        locationMessages = []
        for location in locations:
            locationMessage = location_pb2.LocationMessage()
            locationMessage.id=location[0]
            locationMessage.person_id=location[1]
            locationMessage.latitude=str(location[2])
            locationMessage.longitude=str(location[3])
            locationMessage.creation_time=str(location[4])
            locationMessages.append(locationMessage)

        result = location_pb2.LocationMessageList()
        result.locations.extend(locationMessages)
        return result


# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)


print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
