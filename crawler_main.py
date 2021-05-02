import os
import pandas as pd
from app.modules.scrapers.price_scraper import main
from app.modules.database_module.db import (
    __database__init__,
    update_school,
    get_all_driving_schools,
)

PATH = "app/data/"


__database__init__()

df = pd.read_csv(os.path.join(PATH, "filtered_driving_schools.csv"))

if len(get_all_driving_schools()) == 0:
    for school in df.itertuples():
        update_school(school.id, school)


main()
