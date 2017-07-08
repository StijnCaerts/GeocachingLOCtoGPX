from os.path import isfile, isdir, splitext, join
from os import listdir
import argparse
import xml.etree.ElementTree as ET
from lxml import html
import requests


def hasValidExtension(file):
    filename, ext = splitext(file)
    return ext == '.loc' or ext == '.LOC'


def processFile(file, gpx):
    tree = ET.parse(file)
    root = tree.getroot()

    waypoint = root[0]

    if waypoint.tag == 'waypoint':
        for child in waypoint:
            if child.tag == 'name':
                cacheID = child.attrib['id']
                desc = child.text
            elif child.tag == 'coord':
                latitude = child.attrib['lat']
                longitude = child.attrib['lon']
            elif child.tag == 'type':
                type = child.text
        if cacheID != "" and desc != "" and latitude != "" and longitude != "" and type != "":
            # All variables are set
            print(cacheID, desc, latitude, longitude)
        else:
            print("LOC file is not valid")
            return
    else:
        print("LOC file not valid.")
        return

    # Scrape extra cache information
    url = "http://www.geocaching.com/seek/cache_details.aspx?wp=" + cacheID
    page = requests.get(url)
    htmlTree = html.fromstring(page.content)
    name = htmlTree.xpath('//span[@id="ctl00_ContentBody_CacheName"]/text()')[0]
    ctype = htmlTree.xpath('//p[@class="cacheImage"]/a/img')[0].get('title')
    diff = htmlTree.xpath('//dl/dd/span[@id="ctl00_ContentBody_uxLegendScale"]/img')[0].get('alt').split()[0]
    terr = htmlTree.xpath('//dl/dd/span[@id="ctl00_ContentBody_Localize12"]/img')[0].get('alt').split()[0]
    size = htmlTree.xpath('//span[@class="minorCacheDetails"]/img')[0].get('title').split()[1].title()

    wpt = ET.SubElement(gpx, "wpt", lat=latitude, lon=longitude)
    ET.SubElement(wpt, "name").text = cacheID
    ET.SubElement(wpt, "desc").text = desc

    ET.SubElement(wpt, "url").text = url
    ET.SubElement(wpt, "urlname").text = cacheID
    ET.SubElement(wpt, "sym").text = type
    ET.SubElement(wpt, "type").text = type + "|" + ctype

    # TODO: id, available, archived in cache tag
    cache = ET.SubElement(wpt, "groundspeak:cache")
    ET.SubElement(cache, "groundspeak:name").text = name
    ET.SubElement(cache, "groundspeak:placed_by").text = ""
    ET.SubElement(cache, "groundspeak:owner", ID="").text = ""
    ET.SubElement(cache, "groundspeak:type").text = ctype
    ET.SubElement(cache, "groundspeak:container").text = size
    ET.SubElement(cache, "groundspeak:difficulty").text = diff
    ET.SubElement(cache, "groundspeak:terrain").text = terr
    ET.SubElement(cache, "groundspeak:short_description").text = ""
    ET.SubElement(cache, "groundspeak:long_description").text = ""


################
# MAIN PROGRAM #
################

parser = argparse.ArgumentParser(description="Geocaching LOC to GPX")
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

input_arg = args.input
output_file = args.output

# Construct GPX structure
gpx = ET.Element("gpx")
gpx.set("xmlns:groundspeak","http://www.groundspeak.com/cache/1/0")

if isfile(input_arg) and hasValidExtension(input_arg):
    processFile(input_arg, gpx)
elif isdir(input_arg):
    # do for all LOC files in folder
    for file in listdir(input_arg):
        if hasValidExtension(file):
            path = join(input_arg, file)
            processFile(path, gpx)

# Write out GPX file if not empty
if len(gpx):
    output_tree = ET.ElementTree(gpx)
    output_tree.write(output_file, "UTF-8", True)




