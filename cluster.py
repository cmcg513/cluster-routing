"""
Author: Casey McGinley

Main script for this project. Takes a CSV file of client data, parses it, 
applies k-means clustering to identify optimal routes, and outputs a HTML files
for each route and for a master list
"""

import utm
import math
import csv
import time
from geopy.geocoders import GoogleV3, Nominatim
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as matcol
from motionless import DecoratedMap, AddressMarker
from bs4 import BeautifulSoup
import copy
import sys
import kmeans


def read_csv(filename):
    """
    Reads data from CSV and attempts to translate geo data into usable Google 
    Maps data 

    Returns UTM coordinates and supplementary data
    """
    geocoder = GoogleV3(api_key = "<scrubbed>")
    raw_data = []
    addresses = []
    latlong = []
    partials = []
    x_coords = []
    y_coords = []
    with open(filename,'r') as raw_file:
        i = 0
        reader = csv.reader(raw_file,delimiter=",", quotechar="\"")
        for row in reader:
            # skip header row
            if i == 0:
                i += 1
                continue
            # progress report
            elif i % 10 == 0:
                print(i)
            i += 1

            # keep record of raw data
            raw_data.append(row)

            # translate to a "Google-approved" address (with lat/long)
            address = row[9]
            zip_code = row[8]
            town = row[7]
            query = " ".join([address,town,'NY',zip_code])
            resp = geocoder.geocode(query,timeout=5)
            if resp == None:
                import IPython; IPython.embed()
            addresses.append(resp.address)

            # track latitude and longitude
            lat = resp.latitude
            lon = resp.longitude
            latlong.append([lat,lon])

            # track partial matches
            if 'partial_match' in resp.raw:
                if resp.raw['partial_match']:
                    partials.append((i-1,row,resp))

            # translate lat/long to UTM coords
            # TODO: what are UTM coords?
            utm_coords = utm.from_latlon(lat,lon)
            x = utm_coords[0]
            y = utm_coords[1]
            x_coords.append(x)
            y_coords.append(y)

    # collect extra data
    extra_data = {}
    extra_data['raw'] = raw_data
    extra_data['addr'] = addresses
    extra_data['latlong'] = latlong
    extra_data['partials'] = partials

    return x_coords, y_coords, extra_data


def cluster(filename,k):
    """
    Applies the k-means clustering to a given file

    Returns the list of centroids, the clusters, the cluster map, as well as
    various supplemental data
    """
    # parse the CSV
    x_coords,y_coords,extra = read_csv(filename)

    # join the X/Y coordinates into a numpy array
    data = []
    for i in range(len(x_coords)):
        x = x_coords[i]
        y = y_coords[i]
        data.append(np.array([x,y]))
    data = np.array(data)

    # apply k-means clustering
    result = list(kmeans.find_centers(data,k))

    result.append(extra)
    return tuple(result)


def generate_map_url(addresses, cluster_map, cluster_num):
    """
    Given a cluster, generate a static Google Maps image with a pin for each 
    address

    Returns the URL to this static image
    """
    # get the subset of addresses
    sa = []
    for i in range(len(addresses)):
        if cluster_map[i] == cluster_num:
            sa.append(addresses[i])

    # styling for map
    road_styles = [{
        'feature': 'road.highway',
        'element': 'geomoetry',
        'rules': {
            'visibility': 'simplified',
            'color': '#c280e9'
        }
    }, {
        'feature': 'transit.line',
        'rules': {
            'visibility': 'simplified',
            'color': '#bababa'
        }
    }]

    # get maps
    dmap = DecoratedMap(style=road_styles)

    # add marker for each address
    for a in sa:
        dmap.add_marker(AddressMarker(a))

    return dmap.generate_url()


def collect_map_urls(extra,cluster_map,clusters):
    """
    Iterates over each cluster and gathers the necessary Google Maps URL for
    a static map image
    """
    urls = []
    for key in clusters:
        try:
            urls.append(generate_map_url(extra['addr'],cluster_map,key))
        except:
            # TODO: when are erros generated? Server side with Google Maps?
            import IPython; IPython.embed()
            sys.exit()
    return urls


def get_totals(raw_data):
    """
    Count the number of meals and distinct locations in the raw CSV data

    Returns counts for the meals and the number of distinct locations
    """
    meals = 0
    count = 0
    for row in raw_data:
        count += 1
        meals += int(row[11])
    return meals,count


def generate_master_list(urls,total_meals,total_locs,clusters,cluster_map,raw_data):
    """
    Write the HTML files for individual routes and compile the HTML for the 
    master list

    Returns the HTML for the master list
    """
    # map of indices in a raw CSV row to the field names they correspond to
    field_names = {
        5:'name',
        6:'phone',
        7:'town',
        8:'zip',
        9:'street',
        10:'apt',
        11:'meals',
        12:'instr'
    }

    with open("master_template.html","r") as tmp:
        # Soupify the HTML
        soup = BeautifulSoup(tmp,'html.parser')

        # add the totals counts to their respective tags
        total_meals_tag = soup.find(id="total_meals")
        total_locs_tag = soup.find(id="total_locs")
        total_meals_tag.append(str(total_meals))
        total_locs_tag.append(str(total_locs))

        # grab the data div
        data_div = soup.find(id="data")

        # initialize some counters for a sanity check
        TOTAL_MEAL_SANITY = 0
        TOTAL_ROUTE_SANITY = 0

        # iterate over the centroids/clusters
        # NOTE: mu is an index in to the list of centroids, not the centroid
        # itself
        for mu in clusters:
            print ("cluster "+str(mu+1))

            # Soupify the individual route template
            r_tmp = open("route_template.html","r")
            r_soup = BeautifulSoup(r_tmp, 'html.parser')
            r_data_div = r_soup.find(id="data")

            # identify the indices for the subset of the raw data corresponding
            # to the current centroid
            matching_keys = []
            for i in range(len(cluster_map)):
                if cluster_map[i] == mu:
                    matching_keys.append(i)

            # setup a new div and table for the routing entries
            table_div = soup.new_tag("div",id="table_div"+str(mu),**{'class':"table_div"})
            data_div.append(table_div)
            table = soup.new_tag("table",id="table"+str(mu),**{'class':"table"})
            table_div.append(table)

            # setup the table pre-header
            tr_prehead = soup.new_tag("tr",id="tr_prehead"+str(mu),**{'class':"tr_prehead"})
            table.append(tr_prehead)
            th_prehead = soup.new_tag("th",id="th_prehead"+str(mu),**{'class':"th_prehead"})
            th_prehead.string = "ROUTE #: " + str(mu+1)
            r_title = r_soup.find(id="title_route")
            r_h1 = r_soup.find(id="h1_route")
            r_title.append("ROUTE #: " + str(mu+1))
            r_h1.append("ROUTE #: " + str(mu+1))

            tr_prehead.append(th_prehead)

            # setup the table header
            tr_head = soup.new_tag("tr",id="tr_head"+str(mu),**{'class':"tr_head"})
            table.append(tr_head)
            th = soup.new_tag("th"); th.string = "Name"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Phone"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Town"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Zip"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Street Address"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Apt/Bldg #"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Meals"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Special Intructions"; tr_head.append(th)
            th = soup.new_tag("th"); th.string = "Agency"; tr_head.append(th)

            # initialize a count for the total number of meals
            meal_count = 0

            # create a table row for each client
            tr_list = []
            for key in matching_keys:
                tr = soup.new_tag("tr",id="tr_data"+str(key),**{'class':"tr_data"})
                tr_list.append((raw_data[key][9],tr))

                for i in range(5,13):
                    th = soup.new_tag("th",id="th_"+field_names[i]+str(key),**{'class':"th_"+field_names[i]})
                    th.string = raw_data[key][i]
                    tr.append(th)
                    if i == 11:
                        meal_count += int(raw_data[key][i])

                th = soup.new_tag("th",id="th_agency"+str(key),**{'class':"th_agency"})
                th.string = raw_data[key][1]
                tr.append(th)

            # increment the sanity counters
            TOTAL_MEAL_SANITY += meal_count
            TOTAL_ROUTE_SANITY += len(matching_keys)

            # sort the table rows by street name
            tr_list = sorted(tr_list,key=lambda x: x[0])
            for garbage,tr in tr_list:
                table.append(tr)

            # close the table
            tr_end = soup.new_tag("tr",id="tr_total"+str(mu),**{'class':"tr_total"})
            table.append(tr_end)

            th_end1 = soup.new_tag("th",id="th_total1"+str(mu),**{'class':"th_total1"})
            th_end1.string = "TOTAL MEALS: " + str(meal_count)
            tr_end.append(th_end1)

            th_end2 = soup.new_tag("th",id="th_total2"+str(mu),**{'class':"th_total2"})
            th_end2.string = "TOTAL STOPS: " + str(len(matching_keys))
            tr_end.append(th_end2)

            # get the Google Maps URL for the static map image
            url = urls[mu]
            img_div = soup.new_tag("div",id="img_div"+str(mu),**{'class':"img_div"})
            data_div.append(img_div)

            img = soup.new_tag("img",id="img"+str(mu),src=url,**{'class':"img"})
            img_div.append(img)

            # TODO: figure out why this error check is in place...
            try:
                r_data_div.append(BeautifulSoup(table_div.prettify(),'html.parser'))
                r_data_div.append(BeautifulSoup(img_div.prettify(),'html.parser'))
            except:
                print("copy error")
                import IPython; IPython.embed()
                sys.exit()

            # write the individual route files
            indiv_file = open("route_"+str(mu+1)+".html","w")
            indiv_file.write(r_soup.prettify())
            indiv_file.close()

            # close the template
            r_tmp.close()

            # print our santiy check
            print(TOTAL_MEAL_SANITY)
            print(TOTAL_ROUTE_SANITY)

        # return the HTML for the master list
        return soup.prettify()


def main():
    """
    Main routine
    """
    # cluster data
    centers, clusters, cluster_map, extra = cluster("comb_list.csv",120)
    
    # collect the URLs for the Google Maps images
    urls = collect_map_urls(extra,cluster_map,clusters)

    # get counts for the number of meals and the number of stops
    total_meals, total_locs = get_totals(extra['raw'])

    # Generate HTML for routes
    html = generate_master_list(urls,total_meals,total_locs,clusters,cluster_map,extra['raw'])
    f = open("master.html","w")
    f.write(html)
    f.close()

    # write the list of addresses that could only be partially mapped to a
    # legitimate Google maps address
    f = open("partials.txt","w")
    for line in extra['partials']:
        f.write(str(line)+"\n")
    f.close()


if __name__ == "__main__":
    main()
