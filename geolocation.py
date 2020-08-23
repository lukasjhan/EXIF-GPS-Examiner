import piexif
import folium
from geopy.geocoders import Nominatim
import webbrowser

exif_dict = piexif.load("test.jpg")

lat_ref = ''
lat = 0.0
log_ref = ''
log = 0.0
al = 0.0

for tag in exif_dict["GPS"]:
    if piexif.TAGS["GPS"][tag]["name"] == 'GPSLatitude':
        e = exif_dict["GPS"][tag]
        lat = float(e[0][0]/e[0][1]) + (float(e[1][0]/e[1][1]) / 60) + (float(e[2][0]/e[2][1]) / 3600)
    elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLatitudeRef':
        lat_ref = exif_dict["GPS"][tag]
    elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLongitude':
        e = exif_dict["GPS"][tag]
        log = float(e[0][0]/e[0][1]) + (float(e[1][0]/e[1][1]) / 60) + (float(e[2][0]/e[2][1]) / 3600)
    elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLongitudeRef':
        log_ref = exif_dict["GPS"][tag]
    elif piexif.TAGS["GPS"][tag]["name"] == 'GPSAltitude':
        e = exif_dict["GPS"][tag]
        al = float(e[0]/e[1])

if lat_ref == b'S':
    lat = -lat
if log_ref == b'W':
    log = -log

print(lat, log, al)

my_map = folium.Map(location=[lat, log], zoom_start=20)
my_map.save("test.html")
webbrowser.open("test.html")

geolocator = Nominatim(user_agent="test_app_for_bob")
location = geolocator.reverse(str(lat) + ', ' + str(log), timeout=10)
print(location.address)
print(location.altitude)