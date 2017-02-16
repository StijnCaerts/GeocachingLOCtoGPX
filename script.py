import argparse
import xml.etree.ElementTree as ET
from genericpath import exists

parser = argparse.ArgumentParser(description="Geocaching LOC to GPX")
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

input_file = args.input
output_file = args.output

tree = ET.parse(input_file)
root = tree.getroot()

waypoint = root[0]

if waypoint.tag == 'waypoint':
    for child in waypoint:
        if child.tag == 'name':
            cacheID = child.attrib['id']
            cacheName = child.text
        elif child.tag == 'coord':
            latitude = child.attrib['lat']
            longitude = child.attrib['lon']
    if cacheID != "" and cacheName != "" and latitude != "" and longitude != "":
        # All variables are set
        print(cacheID, cacheName, latitude, longitude)
    else:
        print("LOC file is not valid")
        exit()
else:
    print("LOC file not valid.")
    exit()


gpx = ET.Element("gpx")

wpt = ET.SubElement(gpx, "wpt", lat=latitude, lon=longitude)
ET.SubElement(wpt, "name").text = cacheID
ET.SubElement(wpt, "desc").text = cacheName

ET.SubElement(wpt, "url").text = "http://www.geocaching.com/seek/cache_details.aspx?wp=" + cacheID
ET.SubElement(wpt, "urlname").text = cacheID

output_tree = ET.ElementTree(gpx)
output_tree.write(output_file, "UTF-8", True)
