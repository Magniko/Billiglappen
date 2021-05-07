from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib import request, error, parse
from pydantic import BaseModel, BaseConfig, validator
from app.modules.database_module.db import (
    get_all_driving_schools,
    get_class_prices,
    get_driving_school,
    get_administration_prices,
    get_classes_of_driving_school
)
import haversine as hs
import os
import json
import threading
from app.modules.utils.utils import set_light_class_price, set_tg_price, get_class_prices


classes = {"B", "Ba", "B96", "BE", "A", "A1", "A2", "AM146", "AM147"}


app = FastAPI(  title="Billiglappen.no API",
                description="An API which allows users to query for the total price of nearby driving school packages, and compare them.",
                version="0.2",
            )


# configuring headers for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET, POST"],
    allow_headers=["*"],
)


@app.get("/light_classes")
def endpoint_class_prices(
    class_: str,
    n: int,
    threshold: float,
    lat: float,
    long_: float,
    include_admin_fees: bool = False,
):
    if class_ not in classes:
        raise HTTPException(status_code=400, detail="Class type is not valid")

    driving_schools = [
        school
        for school in get_all_driving_schools()
        if hs.haversine((float(school["lat"]), float(school["long"])), (lat, long_))
        < threshold
    ]


    if include_admin_fees == True:
        admin_fees = sum(get_administration_prices(class_).values())



    result_driving_schools = []

    print(len(driving_schools))

    t_list = []

    for school in driving_schools:
        t = threading.Thread(target=set_light_class_price, args=(school, class_, threshold, n, lat, long_, include_admin_fees, result_driving_schools, ), daemon=True)
        t_list.append(t)
        t.start()


    for t in t_list:
        t.join(5)

    return sorted(result_driving_schools, key=lambda i: i["total_price"])


# for TG-course prices
@app.get("/trafikalt_grunnkurs")
def endpoint_class_prices(
    threshold: float, lat: float, long_: float, over_25: bool = False
):
    driving_schools = [
        school
        for school in get_all_driving_schools()
        if hs.haversine((float(school["lat"]), float(school["long"])), (lat, long_))
        < threshold
    ]

    result_driving_schools = []
    t_list = []

    for school in driving_schools:
        t = threading.Thread(target=set_tg_price, args=(school, threshold, lat, long_, over_25, result_driving_schools, ), daemon=True)
        t_list.append(t)
        t.start()


    for t in t_list:
        t.join(1)

    return sorted(result_driving_schools, key=lambda i: i["tg_package_price"])


@app.get("/naf_vegvesen_gebyrer")
def endpoint_administration_prices():
    return get_administration_prices()

@app.get("/get_class_prices")
def endpoint_get_class_prices(class_id: str):
    prices = get_class_prices(class_id)

    if len(prices) != 0:
        return prices
    else:
        return {"Class not found."}

@app.get("/get_classes_of_driving_school")
def endpoint_get_classes_of_driving_school(school_id: str):
    return get_classes_of_driving_school(school_id)





@app.post("/submit_rating")
def submit_rating():

    return {"why hello there, this is not ready yet. Please stay tuned :)"}
