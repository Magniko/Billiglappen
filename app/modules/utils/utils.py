import os
import json
from urllib import request, error, parse
from app.modules.database_module.db import (
    get_class_prices,
    get_basic_course_prices,
)

API_KEY = os.environ["API_KEY"]


def set_light_class_price(school, class_, threshold, n, lat, long_, include_admin_fees, result_driving_schools):

    distance = get_road_distance(lat, long_, school["place_id"])

    class_id = f"{school['id']}_{class_}".lower()
    if distance < threshold:
        school["distance"] = distance
        class_prices = get_class_prices(class_id)
        if len(class_prices) != 0:
            school = dict(school, **class_prices)
            if n < school["n_lessons"]:
                n = school["n_lessons"]

            school["total_price"] = (
                school["lesson_price"] * (n - chool["n_lessons"])
                + school["package_price"]
                + school["hidden_price"]
            )

            if school["total_price"] != 0:
                if include_admin_fees == True:
                    school["total_price"] += admin_fees
                result_driving_schools.append(school)
    return 0



def set_tg_price(school, threshold, lat, long_, over_25, result_driving_schools):
    distance = get_road_distance(lat, long_, school["place_id"])

    if distance < threshold:
        school["distance"] = distance
        basic_course_prices = get_basic_course_prices(school["id"])
        if len(basic_course_prices) != 0:
            school = dict(school, **basic_course_prices)

            if over_25 == True:
                school["tg_package_price"] = (
                    school["first_aid_price"] + school["night_driving_price"]
                )

            if school["tg_package_price"] != 0:
                result_driving_schools.append(school)

    return 0




def get_road_distance(lat, long_, place_id):

    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = parse.urlencode(
        {
            "units": "metric",
            "origins": f"{lat},{long_}",
            "destinations": f"place_id:{place_id}",
            "key": API_KEY,
        }
    )

    url = f"{base_url}?{params}"

    try:
        r = request.urlopen(url)
        data = json.load(r)

        return float(data["rows"][0]["elements"][0]["distance"]["value"]) / 1000

    except error.URLError as e:
        raise error.URLError(e)
