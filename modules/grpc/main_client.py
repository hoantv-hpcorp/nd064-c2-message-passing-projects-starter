import grpc
import location_pb2
import location_pb2_grpc
# import person_pb2
# import person_pb2_grpc

"""
Sample implementation of a writer that can be used to write messages to gRPC.
"""

print("Sending sample payload...")

channel = grpc.insecure_channel("localhost:5005")
stub = location_pb2_grpc.LocationServiceStub(channel)
# stub = person_pb2_grpc.PersonServiceStub(channel)

# response = stub.Get(person_pb2.Empty())
# print(response)

# locationId = location_pb2.LocationIdMessage(
#     id="30"
# )
# response = stub.GetDetail(locationId)
# print(response)


# locationPrm = location_pb2.FindByPersonAndDatePrm()
# locationPrm.person_id=6
# locationPrm.start_date="2020-01-01"
# locationPrm.end_date="2020-12-30"
# response = stub.FindByPersonAndDate(locationPrm)

locationPrm = location_pb2.FindByDistancePrm()
locationPrm.person_id=5
locationPrm.longitude="37.55363"
locationPrm.latitude="-122.290883"
locationPrm.meters=5
locationPrm.start_date="2020-01-01"
locationPrm.end_date="2020-12-30"
response = stub.FindByDistance(locationPrm)

print(response)


