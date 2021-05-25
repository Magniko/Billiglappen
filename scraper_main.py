import os
import time
import pandas as pd
import logging
from app.modules.scrapers.price_scraper import run_scraper
from app.modules.database_module.db import (
    __database__init__,
    update_school,
    get_all_driving_schools,
    get_class_prices,
)

PATH = "app/data/"

sleep_time = 30*60

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]: %(threadName)s: %(message)s",
    datefmt="%H:%M:%S",
)


logging.debug("Initialising the database.")

__database__init__()

df = pd.read_csv(os.path.join(PATH, "filtered_driving_schools.csv"))

logging.debug("Adding driving schools to database.")
if len(get_all_driving_schools()) == 0:
    for school in df.itertuples():
        update_school(school.id, school)

while True:
	logging.debug("Running scraping session.")
	run_scraper(PATH)
	logging.debug("Sleeping for %d seconds.", sleep_time)
	time.sleep(sleep_time)


