import sqlite3
import os
from datetime import datetime

path = "app/database/"

def __database__init__():

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()

	driving_school_table = """CREATE TABLE IF NOT EXISTS `driving_school` (
	  `driving_school_id` CHAR(12),
	  `name` VARCHAR(128),
	  `website` VARCHAR(128),
	  `address` VARCHAR(128),
	  `municipality` VARCHAR(128),
	  `county` VARCHAR(128),
	  `lat` VARCHAR(128),
	  `long` VARCHAR(128),
	  `phone` INT(32),
	  `rating` FLOAT(2, 1),
	  `place_id` VARCHAR(128),
	  PRIMARY KEY (`driving_school_id`)
	);"""

	light_class_table = """CREATE TABLE IF NOT EXISTS `light_class` (
	  `class_id` CHAR(18),
	  `driving_school_id` CHAR(12),
	  `class` CHAR(5),
	  `package_price` INT(32),
	  `lesson_price` INT(32),
	  `evaluation_price` INT(32),
	  `safety_track_price` INT(32),
	  `safety_road_price` INT(32),
	  `drive_test_price` INT(32),
	  `other_price` INT(32),
	  `hidden_price` INT(32),
	  `discount` INT(32),
	  `n_lessons` INT(32),
	  `passing_rate` FLOAT(4, 3),
	  `last_updated` DATETIME(0),
	  PRIMARY KEY (`class_id`),
	  FOREIGN KEY (`driving_school_id`) REFERENCES driving_school(`driving_school_id`)
	);"""

	basic_course_table = """CREATE TABLE IF NOT EXISTS `basic_course` (
	  `driving_school_id` CHAR(12),
	  `package_price` INT(32),
	  `theory_price` INT(32),
	  `first_aid_price` INT(32),
	  `low_light_price` INT(32),
	  `mc_intro_price` INT(32),
	  `discount` INT(32),
	  `last_updated` DATETIME(0),
	  PRIMARY KEY (`driving_school_id`),
	  FOREIGN KEY (`driving_school_id`) REFERENCES driving_school(`driving_school_id`)
	);"""

	mc_upgrade = """CREATE TABLE IF NOT EXISTS `mc_upgrades` (
	 `class_id` CHAR(15),
     `a1_to_a2` INT(32),
  	 `a2_to_a` INT(32)
  	  PRIMARY KEY (`class_id`),
	  FOREIGN KEY (`class_id`) REFERENCES light_class(`class_id`)
	);"""

	naf_table = """CREATE TABLE IF NOT EXISTS `naf` (
	  `naf` INT(32),
	  `last_updated` DATETIME(0)
	);"""

	vegvesen_table = """CREATE TABLE IF NOT EXISTS `vegvesen` (
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
	cursor.execute(naf_table)
	cursor.execute(vegvesen_table)

	db.commit()


	

def add_school(school):

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()

	values = (school.id, school.name, school.website, school.address, school.municipality, 
	school.county, school.lat, school.long, school.phone_number, school.rating, school.place_id)

	query = f"""INSERT INTO driving_school(driving_school_id, name, website, address, municipality, 
				county, lat, long, phone, rating, place_id)
				VALUES({', '.join([f'"{str(i)}"' for i in values])});"""

	
	cursor.execute(query)
	db.commit()

def update_school(id_, school):

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()

	values = (school.name, school.website, school.address, school.municipality, 
	school.county, school.lat, school.long, school.phone_number, school.rating, school.place_id, id_)

	query = """	UPDATE driving_school
				SET name = ?,
					website = ?,
					address = ?,
					municipality = ?, 
					county = ?, 
					lat = ?, 
					long = ?, 
					phone = ?, 
					rating = ?, 
					place_id = ?
					WHERE driving_school_id = ?"""

	
	cursor.execute(query, values)
	db.commit()

def get_driving_school(id_):

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()


	cursor.execute("SELECT * FROM driving_school WHERE driving_school_id=?", (id_,))
	return cursor.fetchall()

def get_class_prices(class_id):

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()
	keys = (	"package_price",
				"lesson_price",
				"evaluation_price",
				"safety_track_price",
				"safety_road_price",
				"drive_test_price",
				"other_price",
				"hidden_price",
				"discount",
				"n_lessons"
			)

	query = f"""SELECT {", ".join(keys)} FROM light_class WHERE class_id="{class_id}";"""
	cursor.execute(query)
	return cursor.fetchall()




def update_class(ids, prices):

	db = sqlite3.connect(os.path.join(path, "billiglappen.db"))

	cursor = db.cursor()

	class_id = ids[0]

	keys = (
				"package_price",
				"lesson_price",
				"evaluation_price",
				"safety_track_price",
				"safety_road_price",
				"drive_test_price",
				"other_price",
				"hidden_price",
				"discount",
				"n_lessons"
			)


	date = datetime.now().strftime('"%Y-%m-%d %H:%M:%S"')

	class_prices = get_class_prices(class_id)

	#insert row
	if len(class_prices)==0:
			new_prices = tuple(prices.values())

			query = f"""INSERT INTO light_class ( class_id, driving_school_id, class, {', '.join(keys)}, last_updated)
			VALUES({', '.join(f'"{i}"' for i in ids)}, {', '.join([str(i) for i in new_prices])}, {date});""" 
			cursor.execute(query)

			cursor = db.cursor()

			db.commit()


			return 1




	#update row
	else:
		current_prices = dict(zip(keys, class_prices[0]))

		statements = []
		for (prices_k, current_k) in zip(prices.keys(), current_prices.keys()):

			if prices[prices_k] != current_prices[current_k] and prices[prices_k] != float("inf"):

				if 2 > prices[prices_k]/current_prices[current_k] < 0.75:
					#error_handler(something about the price scraped varying too much and should be investigated)

				else:
					statements.append(f'{current_k} = {prices[prices_k]}')



		if len(statements)>0:
			query = f"""UPDATE light_class
			SET {', '.join(statements)}, last_updated = {date}
			WHERE class_id = "{class_id}";"""

			cursor.execute(query)

			cursor = db.cursor()

			db.commit()


			return 2

		else:
			return 0




if __name__ == '__main__':
	__database__init__()