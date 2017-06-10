import argparse
import xml.etree.ElementTree as ET
from lxml import html
import requests

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
        elif child.tag == 'type':
            type = child.text
    if cacheID != "" and cacheName != "" and latitude != "" and longitude != "" and type != "":
        # All variables are set
        print(cacheID, cacheName, latitude, longitude)
    else:
        print("LOC file is not valid")
        exit()
else:
    print("LOC file not valid.")
    exit()

# Scrape extra cache information
url = "http://www.geocaching.com/seek/cache_details.aspx?wp=" + cacheID
page = requests.get(url)
htmlTree = html.fromstring(page.content)
diff = htmlTree.xpath('//dl/dd/span[@id="ctl00_ContentBody_uxLegendScale"]/img')[0].get('alt').split()[0]
terr = htmlTree.xpath('//dl/dd/span[@id="ctl00_ContentBody_Localize12"]/img')[0].get('alt').split()[0]


# Construct GPX file
gpx = ET.Element("gpx")

wpt = ET.SubElement(gpx, "wpt", lat=latitude, lon=longitude)
ET.SubElement(wpt, "name").text = cacheID
ET.SubElement(wpt, "desc").text = cacheName

ET.SubElement(wpt, "url").text = url
ET.SubElement(wpt, "urlname").text = cacheID
ET.SubElement(wpt, "sym").text = type
ET.SubElement(wpt, "type").text = type

# TODO: id, available, archived in cache tag
cache = ET.SubElement(wpt, "groundspeak:cache")
ET.SubElement(cache, "groundspeak:name").text = ""
ET.SubElement(cache, "groundspeak:placed_by").text = ""
ET.SubElement(cache, "groundspeak:owner", ID="").text = ""
ET.SubElement(cache, "groundspeak:type").text = ""
ET.SubElement(cache, "groundspeak:container").text = ""
ET.SubElement(cache, "groundspeak:difficulty").text = diff
ET.SubElement(cache, "groundspeak:terrain").text = terr
ET.SubElement(cache, "groundspeak:short_description").text = ""
ET.SubElement(cache, "groundspeak:long_description").text = ""

output_tree = ET.ElementTree(gpx)
output_tree.write(output_file, "UTF-8", True)
