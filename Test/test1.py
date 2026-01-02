import json

with open("Test\\flight_response.json", "r") as f:
    data = json.load(f)

# print(data['best_flights'])
# for item in data['best_flights']:
    # print(item['name'])
    # print(item['airline'])
    # print(item['arrival_airport'])
    # print(item['duration'])
    # print(item['airplane'])
    # print(item['travel_class'])
    # print(item['price'])
    # print("\n")



for flight in data["best_flights"]:
    price = flight["price"]

    for flight in flight["flights"]:
        print("Departure Airport: ",flight["departure_airport"]["name"])
        print("Airline: " ,flight["airline"])
        print("Arrival Airport: ",flight["arrival_airport"]["name"])
        print("Duration: " ,flight["duration"])
        print("Airplane: " ,flight["airplane"])
        print("Travel Class: " ,flight["travel_class"])
        print(price)
        print()


