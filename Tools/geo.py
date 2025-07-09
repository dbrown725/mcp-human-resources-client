from geopy.geocoders import Nominatim

def get_location_by_city_and_state(city, state):
    geolocator = Nominatim(user_agent="my_geolocator")
    # location = geolocator.geocode("my location")
    location = geolocator.geocode([city, state])
    return location.latitude, location.longitude

if __name__ == "__main__":
    latitude, longitude = get_location_by_city_and_state("Columbus", "Ohio")
    print(f"Latitude: {latitude}, Longitude: {longitude}")