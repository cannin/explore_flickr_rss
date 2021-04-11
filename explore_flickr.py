import flickrapi
import webbrowser
import json
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import xml.dom.minidom as minidom
import datetime
import os 
#from dotenv import find_dotenv, dotenv_values

# LOAD PARAMETERS ----
## General 
#config = dotenv_values(find_dotenv())

#api_key = config['API_KEY']
#api_secret = config['API_SECRET']

code_version = os.getenv('CODE_VERSION')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
max_items = os.getenv('MAX_ITEMS')
output_file = os.getenv('OUTPUT_FILE')

# SET UP ----
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='etree') #json or etree

print('AUTHENTICATE ----')

# Only do this if we don't have a valid token already
if not flickr.token_valid(perms='read'):

    # Get a request token
    flickr.get_request_token(oauth_callback='oob')

    # Open a browser at the authentication URL. Do this however
    # you want, as long as the user visits that URL.
    authorize_url = flickr.auth_url(perms='read')
    webbrowser.open_new_tab(authorize_url)

    # Get the verifier code from the user. Do this however you
    # want, as long as the user gives the application the code.
    verifier = str(input('Verifier code: '))

    # Trade the request token for an access token
    flickr.get_access_token(verifier)

# RUN ----
print('2. RUN')
#rsp = flickr.photos.getInfo(photo_id='7658567128')

rsp_interestingness = flickr.interestingness.getList(per_page=max_items)
#parsed = json.loads(rsp_interestingness.decode('utf-8'))
xml_str = ET.tostring(rsp_interestingness, encoding='unicode')
print(xml_str)

photos_lst = rsp_interestingness.findall('.//photo')
ids = [x.attrib['id'] for x in photos_lst]
titles = [x.attrib['title'] for x in photos_lst]

# GENERATE OUTPUT ----
# RSS Example
# <rss version="2.0">
#     <channel>
#         <title>W3Schools Home Page</title>
#         <link>https://www.w3schools.com</link>
#         <description>Free web building tutorials</description>
#         <lastBuildDate>Sun, 11 Apr 2021 12:43:08 UTC</lastBuildDate>
#         <pubDate>Sun, 11 Apr 2021 12:43:08 UTC</pubDate>
#         <generator>altmetricrssr: 0.0.88</generator>
#         <item>
#             <title>RSS Tutorial</title>
#             <link>https://www.w3schools.com/xml/xml_rss.asp</link>
#             <description>New RSS tutorial on W3Schools</description>
#             <pubDate>Sun, 11 Apr 2021 12:43:08 UTC</pubDate>
#             <guid>http://dx.doi.org/10.1093/bioinformatics/btz906</guid>
#         </item>
#         <item>
#             <title>XML Tutorial</title>
#             <link>https://www.w3schools.com/xml</link>
#             <description>New XML tutorial on W3Schools</description>
#             <pubDate>Sun, 11 Apr 2021 12:43:08 UTC</pubDate>
#             <guid>http://dx.doi.org/10.1093/bioinformatics/btz906</guid>
#         </item>
#     </channel>
# </rss>

## Main feed information
cur_time = datetime.datetime.now(datetime.timezone.utc)
cur_time_str = cur_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

rss = ET.Element('rss', version="2.0")
channel = ET.SubElement(rss, 'channel')
title = ET.SubElement(channel, 'title')
title.text = "Explore Flickr"
link = ET.SubElement(channel, 'link')
link.text = "http://lunean.com/explore_flickr_rss/rss_tmp.xml"
description = ET.SubElement(channel, 'description')
description.text = "Explore Flickr"
last_build_date = ET.SubElement(channel, 'lastBuildDate')
last_build_date.text = cur_time_str
pub_date = ET.SubElement(channel, 'pubDate')
pub_date.text = cur_time_str
generator = ET.SubElement(channel, 'generator')
generator.text = f"explore_flickr: {code_version}"

for i in range(len(ids)):
    try: 
        img_id = ids[i]
        img_title = titles[i]

        if img_title == "":
            img_title = "Untitled"

        rsp_exif = flickr.photos.getExif(photo_id=img_id)
        xml_str = ET.tostring(rsp_exif, encoding='unicode')
        print(xml_str)

        # Example <exif label="Exposure"><raw>text>
        tmp_xpath = './/exif[@label="Exposure"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            shutter_speed = rsp_exif.find(tmp_xpath).text
        else: 
            shutter_speed = "NA"

        tmp_xpath = './/exif[@label="Aperture"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            aperture = rsp_exif.find(tmp_xpath).text
        else: 
            aperture = "NA"

        tmp_xpath = './/exif[@label="ISO Speed"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            iso = rsp_exif.find(tmp_xpath).text
        else: 
            iso = "NA"

        tmp_xpath = './/exif[@label="Focal Length"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            focal_length = rsp_exif.find(tmp_xpath).text
        else:
            focal_length = "NA"

        tmp_xpath = './/exif[@label="Make"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            make = rsp_exif.find(tmp_xpath).text
        else:
            make = "NA"

        tmp_xpath = './/exif[@label="Model"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            model = rsp_exif.find(tmp_xpath).text
        else:
            model = "NA"

        tmp_xpath = './/exif[@label="Exposure Program"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            exposure_program = rsp_exif.find(tmp_xpath).text
        else:
            exposure_program = "NA"

        tmp_xpath = './/exif[@label="Lens Model"]/raw'
        if rsp_exif.find(tmp_xpath) is not None: 
            lens_model = rsp_exif.find(tmp_xpath).text
        else:
            lens_model = "NA"

        rsp_sizes = flickr.photos.getSizes(photo_id=img_id)
        xml_str = ET.tostring(rsp_sizes, encoding='unicode')
        #print(xml_str)
        thumbnail_url = rsp_sizes.find('.//size[@label="Large"]').attrib['source']

        rsp_info = flickr.photos.getInfo(photo_id=img_id)
        xml_str = ET.tostring(rsp_info, encoding='unicode')
        #print(xml_str)
        img_url = rsp_info.find('.//url[@type="photopage"]').text

        item = ET.SubElement(channel, 'item')
        item_title = ET.SubElement(item, 'title')
        item_title.text = img_title
        item_link = ET.SubElement(item, 'link')
        item_link.text = img_url

        item_pub_date = ET.SubElement(item, 'pubDate')
        item_pub_date.text = cur_time_str

        item_guid = ET.SubElement(item, 'guid')
        item_guid.text = img_url

        # aperture, focal_length, shutter_speed, iso
        item_description = ET.SubElement(item, 'description')
        item_description_str = f"Settings: \
<br/> \
Camera Make: {make}; \
Camera Model: {model}; \
Lens Model: {lens_model}; \
<br/> \
Program: {exposure_program}; \
<br/> \
Aperture: {aperture}; \
Focal Length: {focal_length}; \
Shutter: {shutter_speed}; \
ISO: {iso} \
<br/><br/><img src='{thumbnail_url}'/><br/>Image ID: {img_id}"

        print(f"DESCRIPTION: {item_description_str}")
        #item_description_str = "del<br/><img x='del'/>"
        item_description.text = ET.CDATA(item_description_str)
    except: 
        print(f"ERROR: ID: {img_id}")

rss_str = ET.tostring(rss, encoding='unicode')
print(rss_str)

tmp = minidom.parseString(rss_str)
pretty_xml = tmp.toprettyxml(indent="  ", encoding="utf-8")

f = open(output_file, "wb")
f.write(pretty_xml)
f.close()

# IGNORE ----
# my_xml = ET.Element("my_name")
# my_xml.append(CDATA("<p>some text</p>"))

# my_xml_str = ET.tostring(my_xml, encoding='unicode')
# print(my_xml_str)

