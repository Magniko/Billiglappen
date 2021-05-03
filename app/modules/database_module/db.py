import os
import math
import sqlite3
import logging
from datetime import datetime
from app.modules.error_handler.error_handler import price_change


PATH = "app/database/"

keys_school = (
    "id",
    "name",
    "website",
    "address",
    "municipality",
    "county",
    "lat",
    "long",
    "phone_number",
    "rating",
    "place_id",
)

keys_package = (
    "package_price",
    "lesson_price",
    "evaluation_price",
    "safety_track_price",
    "safety_road_price",
    "drive_test_price",
    "other_price",
    "hidden_price",
    "discount",
    "n_lessons",
)

keys_tg = (
    "tg_package_price",
    "theory_price",
    "first_aid_price",
    "night_driving_price",
    "mc_intro_price",
    "moped_intro_price",
    "discount",
)


def __database__init__():

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    driving_school_table = """CREATE TABLE IF NOT EXISTS `driving_school` (
	  `driving_school_id` CHAR(12),
	  `name` VARCHAR(128),
	  `website` VARCHAR(128),
	  `address` VARCHAR(128),
	  `municipality` VARCHAR(128),
	  `county` VARCHAR(128),
	  `lat` FLOAT(8,6),
	  `long` FLOAT(9,6),
	  `phone` INT(32),
	  `rating` FLOAT(2, 1),
	  `place_id` VARCHAR(128),
	  PRIMARY KEY (`driving_school_id`)
	);"""

    light_class_table = """CREATE TABLE IF NOT EXISTS `light_class` (
	  `class_id` CHAR(18),
	  `driving_school_id` CHAR(12),
	  `class` CHAR(5),
	  `package_price` INT(32) DEFAULT 0,
	  `lesson_price` INT(32) DEFAULT 0,
	  `evaluation_price` INT(32) DEFAULT 0,
	  `safety_track_price` INT(32) DEFAULT 0,
	  `safety_road_price` INT(32) DEFAULT 0,
	  `drive_test_price` INT(32) DEFAULT 0,
	  `other_price` INT(32) DEFAULT 0,
	  `hidden_price` INT(32) DEFAULT 0,
	  `discount` INT(32) DEFAULT 0,
	  `n_lessons` INT(32) ,
	  `passing_rate` FLOAT(4, 3),
	  `last_updated` DATETIME(0),
	  PRIMARY KEY (`class_id`),
	  FOREIGN KEY (`driving_school_id`) REFERENCES driving_school(`driving_school_id`)
	);"""

    basic_course_table = """CREATE TABLE IF NOT EXISTS `basic_course` (
	  `driving_school_id` CHAR(12),
	  `tg_package_price` INT(32) DEFAULT 0,
	  `theory_price` INT(32) DEFAULT 0,
	  `first_aid_price` INT(32) DEFAULT 0,
	  `night_driving_price` INT(32) DEFAULT 0,
	  `mc_intro_price` INT(32) DEFAULT 0,
	  `moped_intro_price` INT(32) DEFAULT 0,
	  `discount` INT(32) DEFAULT 0,
	  `last_updated` DATETIME(0),
	  PRIMARY KEY (`driving_school_id`),
	  FOREIGN KEY (`driving_school_id`) REFERENCES driving_school(`driving_school_id`)
	);"""

    mc_upgrade = """CREATE TABLE IF NOT EXISTS `mc_upgrades` (
	 `class_id` CHAR(15),
     `a1_to_a2` INT(32) DEFAULT 0,
  	 `a2_to_a` INT(32) DEFAULT 0
  	  PRIMARY KEY (`class_id`),
	  FOREIGN KEY (`class_id`) REFERENCES light_class(`class_id`)
	);"""

    admin_table = """CREATE TABLE IF NOT EXISTS `administration` (
	  `naf_fee` INT(32),
	  `drive_test_fee` INT(32),
	  `theory_test_fee` INT(32),
	  `issuance_fee` INT(32),
	  `phote_fee` INT(32),
	  `drive_test_fee_mc` INT(32),
	  `drive_test_fee_be` INT(32),
	  `last_updated` DATETIME(0)
	);"""

    cursor.execute(driving_school_table)
    cursor.execute(light_class_table)
    cursor.execute(basic_course_table)
    cursor.execute(admin_table)

    db.commit()


def update_school(school_id, school):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    values = (
        school.id,
        school.name,
        school.website,
        school.address,
        school.municipality,
        school.county,
        school.lat,
        school.long,
        school.phone_number,
        school.rating,
        school.place_id,
    )

    driving_school_data = get_driving_school(school_id)

    # insert row
    if len(driving_school_data) == 0:
        query = f"""INSERT INTO driving_school(
				driving_school_id,
				name, website,
				address,
				municipality, 
				county, 
				lat, 
				long, 
				phone, 
				rating, 
				place_id)
			VALUES({', '.join([f'"{str(i)}"' for i in values])});"""
        cursor.execute(query)

        cursor = db.cursor()

        db.commit()

        return 1

    # update row
    else:
        statements = []

        for (value, current_value_k) in zip(values, driving_school_data.keys()):

            if value != driving_school_data[current_value_k] and not math.isnan(value):
                statements.append(f"{current_value_k} = {value}")

        if len(statements) > 0:
            query = f"""UPDATE driving_school
			SET {', '.join(statements)}
			WHERE driving_school_id = "{school_id}";"""

            cursor.execute(query)

            cursor = db.cursor()

            db.commit()

            return 2

        else:
            return 0


def get_all_driving_schools():

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    cursor.execute("SELECT * FROM driving_school")

    return [dict(zip(keys_school, i)) for i in cursor.fetchall()]


def get_driving_school(id_):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    cursor.execute("SELECT * FROM driving_school WHERE driving_school_id=?", (id_,))

    results = cursor.fetchall()

    if len(results) == 0:
        return []
    else:
        return [dict(zip(keys_school, i)) for i in results][0]


def get_class_prices(class_id):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    query = f"""SELECT {", ".join(keys_package)}, last_updated 
	FROM light_class WHERE class_id="{class_id}";"""

    cursor.execute(query)

    results = cursor.fetchall()

    new_keys = list(keys_package)
    new_keys.append("last_updated")

    if len(results) == 0:
        return []
    else:
        return [dict(zip(new_keys, i)) for i in results][0]


def update_class(ids, prices):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    class_id = ids[0]

    date = datetime.now().strftime('"%Y-%m-%d %H:%M:%S"')

    class_prices = get_class_prices(class_id)

    # insert row
    if len(class_prices) == 0:
        logging.debug("Creating new light class-row for %s.", class_id)

        new_prices = tuple(prices.values())

        query = f"""INSERT INTO light_class ( 
            class_id, 
            driving_school_id, 
            class, {', '.join(keys_package)}, 
            last_updated)
		VALUES({', '.join(f'"{i}"' for i in ids)}, {', '.join([str(i) if i != float("inf") else "0" for i in new_prices])}, {date});"""

        logging.debug("Query: \n%s", query)

        cursor.execute(query)

        cursor = db.cursor()

        db.commit()

        return 1

    # update row
    else:
        # just a variable that previously zipped 2 lists into a dict together when get_class_prices() only returned a list
        # Instead of replacing its references, I just set it equal to class_prices
        current_prices = class_prices

        statements = []
        for (prices_k, current_k) in zip(prices.keys(), current_prices.keys()):

            if prices[prices_k] != current_prices[current_k] and prices[
                prices_k
            ] != float("inf"):
                if (
                    float(current_prices[current_k]) != 0
                    and 2
                    > float(prices[prices_k]) / float(current_prices[current_k])
                    < 0.75
                ):
                    diff = float(prices[prices_k]) / float(current_prices[current_k])
                    price_change(prices_k, prices[prices_k], ids[0], "LIGHT_CLASS", diff)
                else:
                    statements.append(f"{current_k} = {prices[prices_k]}")

        if len(statements) > 0:
            logging.debug("Updating light class-row for %s.", class_id)

            query = f"""UPDATE light_class
			SET {', '.join(statements)}, last_updated = {date}
			WHERE class_id = "{class_id}";"""

            logging.debug("Query: \n%s", query)


            cursor.execute(query)

            cursor = db.cursor()

            db.commit()

            return 2

        else:
            return 0


def get_basic_course_prices(school_id):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    query = f"""SELECT {", ".join(keys_tg)}, last_updated 
	FROM basic_course WHERE driving_school_id="{school_id}";"""

    cursor.execute(query)

    results = cursor.fetchall()

    new_keys = list(keys_tg)
    new_keys.append("last_updated")

    if len(results) == 0:
        return []
    else:
        return [dict(zip(new_keys, i)) for i in results][0]


def update_basic_course(school_id, prices):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    date = datetime.now().strftime('"%Y-%m-%d %H:%M:%S"')

    basic_course_prices = get_basic_course_prices(school_id)

    # insert row
    if len(basic_course_prices) == 0:

        logging.debug("Creating new TG-row for %s.", school_id)

        new_prices = tuple(prices.values())

        query = f"""INSERT INTO basic_course ( 
				driving_school_id, 
				tg_package_price,
				theory_price,
	  			first_aid_price,
	  			night_driving_price,
	  			mc_intro_price,
	  			moped_intro_price,
	  			discount,
	  			last_updated)
			VALUES('{school_id}', {', '.join([str(i) if i != float("inf") else "0" for i in new_prices])}, {date});"""

        logging.debug("Query: \n%s", query)

        cursor.execute(query)

        cursor = db.cursor()

        db.commit()

        return 1

    # update row
    else:
        current_prices = basic_course_prices

        statements = []
        for (prices_k, current_k) in zip(prices.keys(), current_prices.keys()):

            if (
                prices[prices_k] != current_prices[current_k]
                and prices[prices_k] != float("inf")
                and prices[prices_k] != 0
            ):

                if (
                    float(current_prices[current_k]) != 0
                    and 2
                    > float(prices[prices_k]) / float(current_prices[current_k])
                    < 0.75
                ):
                    diff = float(prices[prices_k]) / float(current_prices[current_k])
                    price_change(prices_k, prices[prices_k], school_id, "BASIC_COURSE", diff)
                else:
                    statements.append(f"{current_k} = {prices[prices_k]}")

        if len(statements) > 0:
            logging.debug("Updating TG-row for %s.", school_id)

            query = f"""UPDATE basic_course
			SET {', '.join(statements)}, last_updated = {date}
			WHERE driving_school_id = "{school_id}";"""

            logging.debug("Query: \n%s", query)


            cursor.execute(query)

            cursor = db.cursor()

            db.commit()

            return 2

        else:
            return 0


def update_administration(prices):

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()

    date = datetime.now().strftime('"%Y-%m-%d %H:%M:%S"')

    admin_prices = get_administration_prices()

    # insert row
    if len(admin_prices) == 0:
        new_prices = tuple(prices.values())

        logging.debug("Creating row for administration prices")

        query = f"""INSERT INTO administration( 
			naf_fee,
			drive_test_fee,
			theory_test_fee,
			issuance_fee,
			phote_fee,
			drive_test_fee_mc,
			drive_test_fee_be,
			last_updated )
			VALUES({', '.join([str(i) for i in new_prices])}, {date});"""

        logging.debug("Query: \n%s", query)

        cursor.execute(query)

        cursor = db.cursor()

        db.commit()

        return 1

    # update row
    else:



        current_prices = admin_prices

        statements = []

        for (prices_k, current_k) in zip(prices.keys(), current_prices.keys()):

            if (
                prices[prices_k] != current_prices[current_k]
                and prices[prices_k] != float("inf")
                and prices[prices_k] != 0
            ):

                if (
                    float(current_prices[current_k]) != 0
                    and 2
                    > float(prices[prices_k]) / float(current_prices[current_k])
                    < 0.75
                ):
                    diff = float(prices[prices_k]) / float(current_prices[current_k])
                    price_variance(prices_k, prices[prices_k], "administration", "ADMINISTRATION", diff)

                else:
                    statements.append(f"{current_k} = {prices[prices_k]}")

        if len(statements) > 0:
            logging.debug("Updating row for administration prices")

            query = f"""UPDATE administration
			SET {', '.join(statements)}, last_updated = {date};"""

            logging.debug("Query: \n%s", query)


            cursor.execute(query)

            cursor = db.cursor()

            db.commit()

            return 2

        else:
            return 0


def get_administration_prices(class_=None, with_update=False):

    test = "drive_test_fee"

    if class_ in {"A", "A1", "A2"}:
        test = "drive_test_fee_mc"
    elif class_ == "BE":
        test = "drive_test_fee_be"

    keys_admin = (
        "naf_fee",
        test,
        "theory_test_fee",
        "issuance_fee",
        "phote_fee",
    )
    if class_ == None:
        keys_admin = (
            "naf_fee",
            "drive_test_fee",
            "theory_test_fee",
            "issuance_fee",
            "phote_fee",
            "drive_test_fee_mc",
            "drive_test_fee_be",
        )

    db = sqlite3.connect(os.path.join(PATH, "billiglappen.db"))

    cursor = db.cursor()
    query = f"""SELECT {", ".join(keys_admin)} FROM administration;"""
    if with_update:
        query = f"""SELECT {", ".join(keys_admin)}, last_updated FROM administration;"""

    cursor.execute(query)

    results = cursor.fetchall()

    if len(results) == 0:
        return []
    else:
        return [dict(zip(keys_admin, i)) for i in results][0]


if __name__ == "__main__":
    __database__init__()
