from fastapi import FastAPI
from urllib import request, error, parse
from pydantic import BaseModel, BaseConfig, validator
from app.modules.database_module.db import get_all_driving_schools, get_driving_school, get_class_prices
import haversine as hs
from API_KEY import API_KEY
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


class Price_Query(BaseModel):
	class_: str
	n: int
	threshold: float
	lat: float
	long_: float
	include_authority_fees = False


	@validator("class_")
	def class_is_valid(v):
		if v not in classes:
			raise ValueError("Class type is not valid")
		else:
			return v

app = FastAPI()


@app.post("/light_classes")
def endpoint_class_prices(req: Price_Query):
	driving_schools = [school for school in get_all_driving_schools() \
	if hs.haversine((float(school["lat"]), float(school["long"])), (req.lat, req.long_)) < req.threshold]

	result_driving_schools = []

	base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

	authority = {}

	if req.include_authority_fees == True:
		authority = get_authority_prices(req.class_)


	for school in driving_schools:
		params = parse.urlencode({"units": "metric", "origins": f"{req.lat},{req.long_}", 
			"destinations": f"place_id:{school['place_id']}", "key": API_KEY})
		url = f"{base_url}?{params}"
		try:
			r = request.urlopen(url)
			data = json.load(r)

			distance = float(data["rows"][0]["elements"][0]["distance"]["value"])/1000
			
			class_id = f"{school['id']}_{req.class_}".lower()
			if distance < req.threshold:
				school["distance"] = distance
				class_prices = get_class_prices(class_id)
				if len(class_prices) != 0:
					school = dict(school, **class_prices)
					n = req.n
					if n < school["n_lessons"]:
						n = school["n_lessons"]

					school["total_price"] = school["lesson_price"]*n + \
					school["evaluation_price"]*2 + school["safety_track_price"] + \
					school["safety_road_price"] + school["drive_test_price"] + \
					school["other_price"] + school["hidden_price"] - school["discount"]

					if req.include_authority_fees == True:
						school["total_price"] += (authority["naf_fee"] + authority["drive_test_fee"] + \
							authority["theory_test_fee"] + authority["issuance_fee"] + authority["phote_fee"])
					result_driving_schools.append(school)


		except error.URLError as e:
			raise URLError(e)

		except Exception as e:
			print("Error")
			#error handling module

	return sorted(result_driving_schools, key = lambda i: i["total_price"])


#for TG-course prices
@app.post("/trafikalt_grunnkurs")
def endpoint_class_prices(req: Price_Query):
	driving_schools = [school for school in get_all_driving_schools() \
	if hs.haversine((float(school["lat"]), float(school["long"])), (req.lat, req.long_)) < req.threshold]

	result_driving_schools = []

	base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"


	for school in driving_schools:
		params = parse.urlencode({"units": "metric", "origins": f"{req.lat},{req.long_}", 
			"destinations": f"place_id:{school['place_id']}", "key": API_KEY})
		url = f"{base_url}?{params}"
		try:
			r = request.urlopen(url)
			data = json.load(r)

			distance = float(data["rows"][0]["elements"][0]["distance"]["value"])/1000
			
			########DO SOMETHING HERE


		except error.URLError as e:
			raise URLError(e)

		#except Exception as e:
		#	print("Error")
			#error handling module

	return sorted(result_driving_schools, key = lambda i: i["total_price"])

	




	

@app.post("/submit_rating")
def submit_rating():

	return {"why hello there, this is not ready yet. Please stay tuned :)"}
