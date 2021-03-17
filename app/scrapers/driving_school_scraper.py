import pandas as pd
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time
import re
import hashlib
import unicodedata
import sys




API_KEY = "AIzaSyASmL0LUQcFsr3quETScQ0CHqqQRTkcWtY"


#viken_oslo_locations = ("60.534526,8.206372", "60.434324,9.540372", "59.892722,9.926970", "59.953415,11.045153", "60.142311,11.176861", "59.286386,10.985599")

viken_locations_rural = ("60.861752,8.446758", "60.606641,8.117169", "60.284211,7.924908", "60.604700,8.970068", "60.322310,8.754376", "60.406515,10.067242", "60.314007,9.605022", "60.016271,9.391583", "60.371991,10.903662", "60.088338,10.238989", "59.638808,9.744604", "59.560976,10.859717", "59.813274,11.480444", "59.424335,11.387918", "59.200056,11.058328", "59.109930,11.569193")

viken_locations_urban = ("60.219467,11.430935", "60.128757,11.119912", "60.093171,10.790322", "60.106863,11.444009", "60.013649,11.155618", "59.983435,10.905840", "59.954569,10.724566", "59.906403,10.537798", "59.826431,10.230181", "59.885739,9.917071", "59.847132,10.963519", "59.830572,10.719073", "59.768400,10.521319", "59.671457,10.282366", "60.036977,11.617044")

viken_locations_metro = ("60.017130,10.949448", "59.980737,10.946702", "59.982798,10.864304", "59.986919,10.779160", "59.977988,10.695390", "59.971804,10.615739", "59.930537,11.056200", "59.945679,10.979661", "59.946367,10.894517", "59.936049,10.654191", "59.933985,10.567674", "59.897500,10.617112", "59.891300,10.529221", "59.878209,10.450940", "59.857038,10.659684", "59.851521,10.520982", "59.837723,10.445451", "59.826681,10.773667", "59.828062,10.684403", "59.806658,10.641831", "59.802514,10.472916", "59.789387,10.779160", "59.780403,10.687150", "59.767959,10.611619", "59.758969,10.470170", "59.740289,10.417985", "59.715367,10.492142")

oslo = ("59.959768,10.793215", "59.960112,10.776231", "59.960971,10.760499", "59.962346,10.744363", "59.952892,10.847703", "59.949798,10.824357", "59.948938,10.808908", "59.951916,10.790977", "59.953064,10.778695", "59.953580,10.766679", "59.954268,10.751573", "59.955127,10.736123", "59.953924,10.721017", "59.952549,10.705911", "59.952033,10.690805", "59.956158,10.675355", "59.960283,10.659906", "59.944296,10.844957", "59.941889,10.829164", "59.942232,10.813371", "59.943608,10.793458", "59.945500,10.777665", "59.946703,10.762903", "59.947047,10.747796", "59.947219,10.733033", "59.945328,10.717927", "59.944812,10.701104", "59.936385,10.843927", "59.934493,10.826074", "59.934493,10.811654", "59.936901,10.800668", "59.936213,10.783502", "59.938105,10.768739", "59.939481,10.753976" ,"59.939653,10.739213", "59.938621,10.724450", "59.937245,10.708314", "59.929505,10.856973", "59.928989,10.840493", "59.925720,10.826074", "59.926064,10.811311", "59.929505,10.795518", "59.927785,10.781785", "59.929333,10.768052", "59.931569,10.754319", "59.932257,10.741617", "59.931397,10.727540", "59.930365,10.715867", "59.929732,10.701370", "59.923244,10.867616", "59.921179,10.852510", "59.920663,10.840837", "59.918254,10.825731", "59.918770,10.811654", "59.921007,10.797578", "59.920319,10.782472", "59.920319,10.768739", "59.922039,10.757409", "59.923072,10.746423", "59.923760,10.734063", "59.922384,10.720331", "59.922900,10.707284", "59.921867,10.691491", "59.912575,10.837747", "59.909648,10.822984", "59.910165,10.808221", "59.912230,10.795862", "59.912230,10.783502", "59.912230,10.771486", "59.913607,10.756379", "59.915500,10.743676", "59.917172,10.727119", "59.914296,10.711747", "59.914640,10.694925", "59.914246,10.680771", "59.911198,10.664026", "59.901729,10.816461", "59.902418,10.801355", "59.903795,10.788652", "59.904656,10.773889", "59.905345,10.758096", "59.907239,10.743333", "59.909304,10.722734", "59.905517,10.691148", "59.905689,10.677758", "59.903451,10.665399", "59.893981,10.806505", "59.895531,10.790368", "59.896736,10.777322", "59.897253,10.762559", "59.897769,10.687028", "59.896220,10.670549", "59.886403,10.797856", "59.887436,10.784810", "59.888642,10.771077", "59.889159,10.755971", "59.878134,10.790647", "59.879857,10.773824", "59.871758,10.784124", "59.869346,10.771421", "59.862968,10.784124", "59.850383,10.781377", "59.946636,10.608751", "59.922212,10.611841", "59.906378,10.569955", "59.911025,10.556909")

counties = ("VIKEN", "OSLO")






def Main():
	"""hello :) """
	#initializing dataframe
	df = pd.DataFrame(columns=["id", "name", "website", "address", "municipalty", "county", "lat", "long", "phone_number", "rating", "place_id"])
	place_ids = []
	if len(sys.argv) <= 1:
		#get place_ids of driving schools and remove duplicates
		place_ids = scrape(viken_locations_rural, 25000) + scrape(viken_locations_urban, 10000) + scrape(viken_locations_metro, 2500) + scrape(oslo, 500)
		place_ids = list(set(place_ids))

		#save place_ids for future use
		with open("place_ids.txt", 'w') as f:
			for i in place_ids:
				f.write('%s\n' % i)
	else:
		with open ("place_ids.txt", 'r') as f:
			place_ids = f.read().splitlines()

	#get postal codes not in Oslo and Viken
	ignore_codes = get_postal_codes(counties)

	
	#get details for each driving school
	for place_id in place_ids:

		data = get_details(place_id)

		#only interested in driving schools that has a website, and are not outside Viken&Oslo
		if data["address_components"][-1]["long_name"] not in ignore_codes and \
		"website" in data:

			#initializing row to be added to dataframe
			row = {"id": get_id(data["name"], data["address_components"][-4]["long_name"]), \
			"name": data["name"], "website": data["website"].replace("www.", '').replace("https://", '').replace("http://", ''), "address": data["formatted_address"].replace(", Norway", ''), \
			"municipalty": data["address_components"][-4]["long_name"], "county": data["address_components"][-3]["long_name"], \
			 "lat": data["geometry"]["location"]["lat"], "long": data["geometry"]["location"]["lng"], "place_id": place_id}
			print(row["id"])
			#optional data to add if it exists
			if "formatted_phone_number" in data:
				row["phone_number"] = data["formatted_phone_number"]

			if "rating" in data:
				row["rating"] = data["rating"]

			print(row)
			df = df.append(row, ignore_index=True)
	print(df)

	#saving the csv
	df.to_csv("driving_schools.csv", index=None)


def scrape(locations, radius=25000):
	place_ids = []

	for location in locations:
			first_page = get_place_id(location, radius, place_ids)
			place_ids.extend([i["place_id"] for i in first_page["results"] if i["business_status"]!="CLOSED_PERMANENTLY"])

			if "next_page_token" in first_page:
				pagetoken = first_page["next_page_token"]

				#this is needed to avoid being denied scraping the next page
				delay = 3


				while pagetoken:
					time.sleep(delay)
					page = get_place_id(location, radius, place_ids, pagetoken)

					place_ids.extend([i["place_id"] for i in page["results"]])

					if "next_page_token" in page:
						pagetoken = page["next_page_token"]

					else:
						pagetoken = None
	return place_ids


def get_place_id(location, radius=25000, place_ids=[], pagetoken=None):
	base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

	if pagetoken:
		params = urllib.parse.urlencode({"location": location, "radius": str(radius), "keyword": "trafikkskole", "key": API_KEY, "pagetoken": pagetoken})

	else:
		params = urllib.parse.urlencode({"location": location, "radius": str(radius), "keyword": "trafikkskole", "key": API_KEY})
	
	url = f"{base_url}?{params}"

	print(url)



	try:
		r = urllib.request.urlopen(url)
		return json.load(r)

	except urllib.error.URLError as e:
		print(e)
		return {"null"}




def get_details(place_id):
	base_url = "https://maps.googleapis.com/maps/api/place/details/json"
	
	#using safe argument to escape commas
	params = urllib.parse.urlencode({"place_id": place_id, "fields": "name,website,formatted_address,address_components,geometry,formatted_phone_number,rating", "key": API_KEY}, safe=",")
	url = f"{base_url}?{params}"

	print(url)

	try:
		r = urllib.request.urlopen(url)
		result = json.load(r)
		return result["result"]

	except urllib.error.URLError as e:
		print(e)
		return get_details(place_id)


def get_postal_codes(counties):
	counties = set([i.upper() for i in counties])

	codes = set()

	url = "http://adressesok.posten.no/api/v1/postal_codes.xml?postal_code=*"

	try:
		r = urllib.request.urlopen(url)
	except urllib.error.URLError as e:
		print(e)
		return {"null"}

	tree = ET.parse(r)
	root = tree.getroot()
	for postal_code in root.findall("postal_code"):
		if postal_code.find("primary_county").text.strip() not in counties:
			codes.add(postal_code.find("postal_code").text)

	return codes

def get_id(school, municipality):
	limit = 8
	string = " ".join([school, municipality]).lower().replace('æ', "ae").replace('ø', "oe").replace('å', "aa")
	id_string = re.sub(r"[^A-Za-z0-9 ]+", '', string).split()

	print(id_string)


	n = int(1+round(limit/(len(id_string))))
	print(n)
	if n <=1:
		n = 2

	id_ = "".join([i[:n] for i in id_string])

	print(" ".join(id_string))

	#using modulo to get just 4 digits of the hash
	id_number = str(int(hashlib.sha256(" ".join(id_string).encode('utf-8')).hexdigest(), 16))[-4:]

	id_ = id_[:limit]

	id_+=str(id_number)


	return id_


if __name__ == "__main__":
	Main()