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

def cluster_points(X, mu):
    cluster_map = []
    clusters  = {}
    for x in X:
        bestmukey = min([(i[0], np.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        cluster_map.append(bestmukey)
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    print(len(clusters.keys()))
    return clusters, cluster_map
 
def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 
def has_converged(mu, oldmu):
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))
 

def find_centers(X, K):
    print("size k " + str(K))
    # Initialize to K random centers
    X = list(X)
    for i in range(len(X)):
        x = X[i]
        x = list(x)
        X[i] = x
    oldmu = random.sample(X, K)
    print("len oldmu " + str(len(oldmu)))
    mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        X = np.array(X)
        clusters, cluster_map = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    print("len final mu " + str(len(mu)))
    print("len clusters " + str(len(clusters.keys())))
    return(mu, clusters, cluster_map)

def read_csv(filename):
    # geocoder = GoogleV3()
    geocoder = GoogleV3(api_key = "<scrubbed>")
    # geocoder = Nominatim()
    raw_data = []
    addresses = [] #?
    latlong = []
    partials = []
    x_coords = []
    y_coords = []
    with open(filename,'r') as raw_file:
        i = 0
        reader = csv.reader(raw_file,delimiter=",", quotechar="\"")
        for row in reader:
            if i == 0:
                i += 1
                continue
            elif i % 10 == 0:
                print(i)
                # time.sleep(3)
            i += 1
            raw_data.append(row)
            address = row[9]
            zip_code = row[8]
            town = row[7]
            query = " ".join([address,town,'NY',zip_code])
            resp = geocoder.geocode(query,timeout=5)
            # import IPython; IPython.embed()
            if resp == None:
                # continue
                import IPython; IPython.embed()
            addresses.append(resp.address)
            lat = resp.latitude
            lon = resp.longitude
            latlong.append([lat,lon])
            # commented out since I timed out for Google
            if 'partial_match' in resp.raw:
                if resp.raw['partial_match']:
                    partials.append((i-1,row,resp))
            utm_coords = utm.from_latlon(lat,lon)
            x = utm_coords[0]
            y = utm_coords[1]
            x_coords.append(x)
            y_coords.append(y)
    extra_data = {}
    extra_data['raw'] = raw_data
    extra_data['addr'] = addresses
    extra_data['latlong'] = latlong
    extra_data['partials'] = partials
    return x_coords, y_coords, extra_data

def cluster(filename,k):
    x_coords,y_coords,extra = read_csv(filename)
    data = []
    for i in range(len(x_coords)):
        x = x_coords[i]
        y = y_coords[i]
        data.append(np.array([x,y]))
    data = np.array(data)
    result = list(find_centers(data,k))
    result.append(extra)
    return tuple(result)

def generate_map_url(addresses, cluster_map, cluster_num):
    sa = []
    for i in range(len(addresses)):
        if cluster_map[i] == cluster_num:
            sa.append(addresses[i])

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
    dmap = DecoratedMap(style=road_styles)
    for a in sa:
        dmap.add_marker(AddressMarker(a))
    return dmap.generate_url()

def collect_map_urls(extra,cluster_map,clusters):
    urls = []
    for key in clusters:
        try:
            urls.append(generate_map_url(extra['addr'],cluster_map,key))
        except:
            import IPython; IPython.embed()
            # continue
            sys.exit()
    # import IPython; IPython.embed()
    return urls

def get_totals(raw_data):
    meals = 0
    count = 0
    for row in raw_data:
        count += 1
        meals += int(row[11])
    return meals,count

def generate_master_list(urls,total_meals,total_locs,clusters,cluster_map,raw_data):
    field_names = {5:'name',6:'phone',7:'town',8:'zip',9:'street',10:'apt',11:'meals',12:'instr'}
    with open("master_template.html","r") as tmp:
        soup = BeautifulSoup(tmp,'html.parser')

        total_meals_tag = soup.find(id="total_meals")
        total_locs_tag = soup.find(id="total_locs")
        total_meals_tag.append(str(total_meals))
        total_locs_tag.append(str(total_locs))

        data_div = soup.find(id="data")
        TOTAL_MEAL_SANITY = 0
        TOTAL_ROUTE_SANITY = 0
        for mu in clusters:
            print ("cluster "+str(mu+1))
            r_tmp = open("route_template.html","r")
            r_soup = BeautifulSoup(r_tmp, 'html.parser')
            r_data_div = r_soup.find(id="data")

            matching_keys = []
            for i in range(len(cluster_map)):
                if cluster_map[i] == mu:
                    matching_keys.append(i)

            table_div = soup.new_tag("div",id="table_div"+str(mu),**{'class':"table_div"})
            data_div.append(table_div)

            table = soup.new_tag("table",id="table"+str(mu),**{'class':"table"})
            table_div.append(table)

            tr_prehead = soup.new_tag("tr",id="tr_prehead"+str(mu),**{'class':"tr_prehead"})
            table.append(tr_prehead)
            th_prehead = soup.new_tag("th",id="th_prehead"+str(mu),**{'class':"th_prehead"})
            th_prehead.string = "ROUTE #: " + str(mu+1)
            # import IPython; IPython.embed()
            r_title = r_soup.find(id="title_route")
            r_h1 = r_soup.find(id="h1_route")
            r_title.append("ROUTE #: " + str(mu+1))
            r_h1.append("ROUTE #: " + str(mu+1))

            tr_prehead.append(th_prehead)

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

            meal_count = 0
            tr_list = []
            for key in matching_keys:
                tr = soup.new_tag("tr",id="tr_data"+str(key),**{'class':"tr_data"})
                tr_list.append((raw_data[key][9],tr))

                for i in range(5,13):
                    th = soup.new_tag("th",id="th_"+field_names[i]+str(key),**{'class':"th_"+field_names[i]})
                    th.string = raw_data[key][i]
                    tr.append(th)
                    if i == 11:
                        # print(raw_data[key])
                        # import IPython; IPython.embed()
                        meal_count += int(raw_data[key][i])

                th = soup.new_tag("th",id="th_agency"+str(key),**{'class':"th_agency"})
                th.string = raw_data[key][1]
                tr.append(th)
            TOTAL_MEAL_SANITY += meal_count
            TOTAL_ROUTE_SANITY += len(matching_keys)

            tr_list = sorted(tr_list,key=lambda x: x[0])
            for garbage,tr in tr_list:
                table.append(tr)

            tr_end = soup.new_tag("tr",id="tr_total"+str(mu),**{'class':"tr_total"})
            table.append(tr_end)

            th_end1 = soup.new_tag("th",id="th_total1"+str(mu),**{'class':"th_total1"})
            th_end1.string = "TOTAL MEALS: " + str(meal_count)
            tr_end.append(th_end1)

            th_end2 = soup.new_tag("th",id="th_total2"+str(mu),**{'class':"th_total2"})
            th_end2.string = "TOTAL STOPS: " + str(len(matching_keys))
            tr_end.append(th_end2)

            url = urls[mu]
            img_div = soup.new_tag("div",id="img_div"+str(mu),**{'class':"img_div"})
            data_div.append(img_div)

            img = soup.new_tag("img",id="img"+str(mu),src=url,**{'class':"img"})
            img_div.append(img)

            try:
                r_data_div.append(BeautifulSoup(table_div.prettify(),'html.parser'))
                r_data_div.append(BeautifulSoup(img_div.prettify(),'html.parser'))
            except:
                print("copy error")
                import IPython; IPython.embed()
                sys.exit()
            indiv_file = open("route_"+str(mu+1)+".html","w")
            indiv_file.write(r_soup.prettify())
            indiv_file.close()
            r_tmp.close()
            print(TOTAL_MEAL_SANITY)
            print(TOTAL_ROUTE_SANITY)
        # import IPython; IPython.embed()
        return soup.prettify()
            # url = urls[mu]



def main():
    # centers,clusters,cluster_map,extra = cluster('sample.csv',5)
    # centers,clusters,cluster_map,extra = cluster('raw_data.csv',100)
    # centers,clusters,cluster_map,extra = cluster('sample2.csv',20)
    centers,clusters,cluster_map,extra = cluster("comb_list.csv",120)
    # import IPython; IPython.embed()
    # return
    urls = collect_map_urls(extra,cluster_map,clusters)
    total_meals,total_locs = get_totals(extra['raw'])
    html = generate_master_list(urls,total_meals,total_locs,clusters,cluster_map,extra['raw'])
    f = open("master.html","w")
    f.write(html)
    f.close()

    f = open("partials.txt","w")
    for line in extra['partials']:
        f.write(str(line)+"\n")
    f.close()



main()