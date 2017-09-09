"""
Author: Casey McGinley

Script testing out the Google Maps API
"""

import utm
import math
import csv
import time
from geopy.geocoders import GoogleV3

geocoder = GoogleV3()

f = open('raw_data.csv','r')
reader = csv.reader(f, delimiter=",", quotechar="\"")
out = open('latlon.csv','w')
i = 0
raw_data = []
adresses = []
latlong = []
partials = []
for vals in reader:
	if i == 0:
		i += 1
		continue
	elif i % 10 == 0:
		print(i)
		time.sleep(1)
	i += 1
	# vals = line.split(",")
	raw_data.append(vals)
	address = vals[9]
	zip_code = vals[8]
	town = vals[7]
	query = " ".join([address,town,'NY',zip_code])
	resp = geocoder.geocode(query)
	if resp == None:
		import IPython; IPython.embed()
	lat = resp.latitude
	lon = resp.longitude
	if 'partial_match' in resp.raw:
		if resp.raw['partial_match']:
			partials.append((raw_data,resp))
	utm_coords = utm.from_latlon(lat,lon)
	x = utm_coords[0]
	y = utm_coords[1]
	out.write(",".join([str(x),str(y)])+"\n")
f.close()
out.close()



