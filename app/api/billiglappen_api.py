from fastapi import FastAPI
from urllib import request, error, parse
from pydantic import BaseModel, BaseConfig, validator
from app.modules.database_module.db import get_all_driving_schools, get_driving_school, get_class_prices, get_basic_course_prices, get_administration_prices
import haversine as hs
import os
import json



classes = 	{
				"B",
				"Ba",
				"B96",
				"BE",
				"A",
				"A1",
				"A2",
				"AM146",
				"AM147"
			}



app = FastAPI()

API_KEY = os.environ['API_KEY']

#configuring headers for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET, POST"],
    allow_headers=["*"],
)


@app.get("/light_classes")
def endpoint_class_prices(class_: str, n: int, threshold: float, lat: float, long_: float, include_admin_fees: bool=False):
	if class_ not in classes:
		raise ValueError("Class type is not valid")

	driving_schools = [school for school in get_all_driving_schools() \
	if hs.haversine((float(school["lat"]), float(school["long"])), (lat, long_)) < threshold]

	result_driving_schools = []

	base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"


	if include_admin_fees == True:
		admin_fees = sum(get_administration_prices(class_).values())


	for school in driving_schools:
		params = parse.urlencode({"units": "metric", "origins": f"{lat},{long_}", 
			"destinations": f"place_id:{school['place_id']}", "key": API_KEY})
		url = f"{base_url}?{params}"
		try:
			r = request.urlopen(url)
			data = json.load(r)

			distance = float(data["rows"][0]["elements"][0]["distance"]["value"])/1000
			
			class_id = f"{school['id']}_{class_}".lower()
			if distance < threshold:
				school["distance"] = distance
				class_prices = get_class_prices(class_id)
				if len(class_prices) != 0:
					school = dict(school, **class_prices)
					if n < school["n_lessons"]:
						n = school["n_lessons"]

					school["total_price"] = school["lesson_price"]*n + \
					school["evaluation_price"]*2 + school["safety_track_price"] + \
					school["safety_road_price"] + school["drive_test_price"] + \
					school["other_price"] + school["hidden_price"] - school["discount"]

					if include_admin_fees == True:
						school["total_price"] += admin_fees
					result_driving_schools.append(school)


		except error.URLError as e:
			raise URLError(e)

		#except Exception as e:
		#	print("Error")
			#error handling module

	return sorted(result_driving_schools, key = lambda i: i["total_price"])


#for TG-course prices
@app.get("/trafikalt_grunnkurs")
def endpoint_class_prices(threshold: float, lat: float, long_:float, over_25: bool=False):
	driving_schools = [school for school in get_all_driving_schools() \
	if hs.haversine((float(school["lat"]), float(school["long"])), (lat, long_)) < threshold]

	result_driving_schools = []

	base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"


	for school in driving_schools:
		params = parse.urlencode({"units": "metric", "origins": f"{lat},{long_}", 
			"destinations": f"place_id:{school['place_id']}", "key": API_KEY})
		url = f"{base_url}?{params}"
		try:
			r = request.urlopen(url)
			data = json.load(r)

			distance = float(data["rows"][0]["elements"][0]["distance"]["value"])/1000
			if distance < threshold:
				school["distance"] = distance
				basic_course_prices = get_basic_course_prices(school["id"])
				if len(basic_course_prices) != 0:
					school = dict(school, **basic_course_prices)

					if over_25 == True:
						school["tg_package_price"] = school["first_aid_price"] + school["night_driving_price"]

					result_driving_schools.append(school)




		except error.URLError as e:
			raise URLError(e)

		#except Exception as e:
		#	print("Error")
			#error handling module

	return sorted(result_driving_schools, key = lambda i: i["tg_package_price"])

	


@app.get("/naf_vegvesen_gebyrer")
def endpoint_administration_prices():
	return get_administration_prices()

	

@app.post("/submit_rating")
def submit_rating():

	return {"why hello there, this is not ready yet. Please stay tuned :)"}
