import re
import pandas as pd
import urllib.error
import urllib.parse
import urllib.request
from lxml import html 
import lxml
import time
import threading
import logging
import sqlite3
import sys
import glob
import os
from app.modules.database_module.db import update_class

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s]: %(threadName)s: %(message)s", datefmt="%H:%M:%S")
start = time.time()

n_lessons_ = {	"B": 10,
				"B_1": 10,
				"Ba": 10,
				"Ba_1": 10,
				"B96": 4,
				"BE": 4,
				"A": 5,
				"A1": 8,
				"A2": 5,
				"AM146": 5,
				"AM147": 5
				}

def Main(tag=None, school=None):
	#while(True):

	data_path = "app/data"
	files = glob.glob(os.path.join(data_path, "light_classes_xpaths/*.csv"))

	columns = (
			"id",
			"name",
			"website",
			"price_url",
			"type",
			"lesson_xpath",
			"evaluation_xpath",
			"track_xpath",
			"road_xpath",
			"test_xpath",
			"other_xpath",
			"hidden_xpath",
			"a12_xpath",
			"a2a_xpath",
			"package_price",
			"n_lessons",
			"comment"
	)

	frames = []
	df = pd.DataFrame(columns=columns)
	for filename in files:
		frame = pd.read_csv(filename, header=0)
		frames.append(frame)


	if 0==0:
		if school != None:
			frames = pd.read_csv(os.path.join(data_path, f"light_classes_xpaths/{school}_light_classes.csv"))

		df = df.append(frames, ignore_index=True)

		tg = pd.read_csv(os.path.join(data_path, "tg_driving_schools_asker.csv"))


		#if tag != "tg":
		for class_ in df.itertuples(index=None):
			t = threading.Thread(target=scrape_light_classes, args=(class_, ))
			t.start()
		#else:
		#	for basic in tg.itertuples(index=None):
		#		t = threading.Thread(target=scrape_tg, args=(basic, ))
		#		t.start()


def scrape_light_classes(class_):
		logging.debug("Starting scraping of %s, %s on thread...", class_.price_url, class_.name)


		url = format_url(class_.price_url)
		r = urllib.request.urlopen(url)
		try:
			tree = lxml.html.fromstring(r.read())
		except:
			error_handler(5, [url])

		with_naf = False
		naf_fee = 1300

		from_front = False

		keys = 	(	
					"package_price",
					"lesson",
					"evaluation",
					"track",
					"road",
					"test",
					"other",
					"hidden",
					"discount",
					"n_lessons"
				)

		mc_upgrade_keys = 	(
								"a12",
								"a2a"
							)


		prices = dict.fromkeys(keys)

		mc_upgrade_prices = dict.fromkeys(mc_upgrade_keys)

		for i in range(5, len(class_)-3):
			price = 0

			if not pd.isnull(class_[i]):

				price_xpath = class_[i]
				

				div = 1


				if "_NOT_XPATH" in price_xpath:
					price = int(re.sub("[^0-9]", '', price_xpath))

				else:
					if "_DIV" in price_xpath:
						div = int(price_xpath.split("_DIV_")[-1])
						price_xpath = price_xpath.split("_DIV_")[0]
					if "_WITH_NAF" in price_xpath:
						with_naf = True
						price_xpath = price_xpath.replace("_WITH_NAF", '')
					if "_FRONT" in price_xpath:
						from_front = True
						price_xpath = price_xpath.replace("_FRONT", '')


					xpath = price_xpath.split()
					e_info = (url, class_._fields[i])

					if with_naf and class_._fields[i] == "track_xpath":
						price = int(sum([parse_xpath(xp, tree, e_info, from_front) for xp in xpath])/div - naf_fee)
					else:
						price = int(sum([parse_xpath(xp, tree, e_info, from_front) for xp in xpath])/div)
					


			else:
				price = 0

			if class_._fields[i] == "a12_xpath" or class_._fields[i] == "a2a_xpath":
				mc_upgrade_prices[class_._fields[i].replace("_xpath", '')] = price
			else:
				prices[class_._fields[i].replace("_xpath", '')] = price



		package_price = 0
		n = n_lessons_[class_.type]
		with_test = True
		front_package = False

		package_price_xpath = class_.package_price


		if "_NOT_XPATH" in package_price_xpath:
			package_price = int(re.sub("[^0-9]", '', package_price_xpath))
		elif package_price_xpath == "NO_PACK":
			package_price = prices["evaluation"]*2 + prices["track"] + prices["road"] + prices["test"]
		else:
			if "_NO_TEST" in package_price_xpath:
				package_price_xpath = package_price_xpath.replace("_NO_TEST", '')
				with_test = False
			if "_FRONT" in package_price_xpath:
				package_price_xpath = package_price_xpath.replace("_FRONT", '')
				front_package = True

			package_price = parse_xpath(package_price_xpath, tree, [url, "package_price"], front_package)

		prices["package_price"] = package_price

		pre_discount_package_price = 0

		if with_test:
			pre_discount_package_price = prices["lesson"]*int(class_.n_lessons) + prices["evaluation"]*2 + prices["track"] + prices["road"] + prices["test"] + prices["other"]
		else:
			pre_discount_package_price = prices["lesson"]*int(class_.n_lessons) + prices["evaluation"]*2 + prices["track"] + prices["road"] + prices["other"]


		#add the NAF fee if applicable to the pre-discount price to get a proper discount
		if with_naf:
			pre_discount_package_price+=naf_fee

		discount = pre_discount_package_price - package_price

		#instead of adding alot of extra complexity in case a driving school only offer a package and no unbundled prices
		#which results in there being no pre_discount_package_price, the discount is just set to 0 if it is the negative equal of package price
		no_prices = False
		if -discount == package_price:
			no_prices = True
			discount = 0
		
		prices["discount"] = discount
		prices["n_lessons"] = class_.n_lessons

		class_id = f"{class_.id}_{class_.type.lower()}"
		ids = [class_id, class_.id, class_.type]

		#print(prices)

		msg = update_class(ids, prices)
		if msg == 0:
			logging.debug("No new prices of %s.", class_.name)
		elif msg == 1:
			logging.debug("Added new row of class %s to %s.", class_.type, class_.name)
		elif msg == 2:
			logging.debug("Updated price of class  %s for %s.", class_.type, class_.name)
		elif msg == -1:
			logging.debug("Error, scraper got an illegal value. Class %s for %s.", class_.type, class_.name)







		#tot_price = 0
		#if no_prices:
		#	tot_price =  prices["lesson"]*n + package_price

		#else:
		#	tot_price =  prices["lesson"]*n + prices["evaluation"]*2 + prices["track"] + prices["road"] + prices["test"] + prices["other"]  + prices["hidden"] - discount
		
		#print(class_.name)
		#print(prices)

		#logging.debug("Price of lesson for %s: %d", class_.type, prices["lesson"])
		#logging.debug("Price of evaluation for %s: %d", class_.type, prices["evaluation"])
		#logging.debug("Price of track for %s: %d", class_.type, prices["track"])
		#logging.debug("Price of road for %s: %d", class_.type, prices["road"])
		#logging.debug("Price of test for %s: %d", class_.type, prices["test"])

		#logging.debug("Pre-dicount price of %s: %d", class_.type, pre_discount_package_price)
		#logging.debug("Discount of %s: %d", class_.type, discount)
		#logging.debug("Package price %s: %d", class_.type, package_price)
		#print(class_.name)
		#logging.debug("Total Price with %d lessons %s: %d", n, class_.type, tot_price)
		#print()





def scrape_tg(school):
		logging.debug("Starting scraping of %s, % on thread...", school.price_url, school.name)

		url = format_url(school.price_url)

		r = urllib.request.urlopen(url)
		try:
			tree = lxml.html.fromstring(r.read())
		except:
			error_handler(5, [url])

		prices = {}

		for i in range(4, len(school)-1):
			if not pd.isnull(school[i]):

				price_xpath = school[i]





				if "_NOT_XPATH" in price_xpath:
					price = int(re.sub("[^0-9]", '', price_xpath))

				else:
					if "_FRONT" in price_xpath:
						from_front = True
						price_xpath = price_xpath.replace("_FRONT", '')


					xpath = price_xpath.split()
					e_info = (url, school._fields[i])

					price = int(sum([parse_xpath(xp, tree, e_info, from_front) for xp in xpath]))

				prices[school._fields[i].replace("_xpath", '')] = price


			else:
				prices[school._fields[i].replace("_xpath", '')] = 0


		tg_package_price = 0
		
		if "_NOT_XPATH" in school.tg_package_price:
			tg_package_price = int(re.sub("[^0-9]", '', school.tg_package_price))
		
		elif school.tg_package_price == "NO_PACK":
			tg_package_price = prices["theory"] + prices["night"]
		
		else:
			tg_package_price = parse_xpath(school.tg_package_price, tree, [url, "tg_package_price"])
		

		tg_pre_discount_under_25 = prices["theory"] + prices["night"]
		tg_package_over_25 = prices["firstaid"] + prices["night"]
		tg_discount_under_25 = tg_pre_discount_under_25 - tg_package_price

		print(school.name)
		print(prices)
		#logging.debug("Price of theory for %s: %d", school.id, prices["theory"])
		#logging.debug("Price of firstaid for  %s: %d", school.id, prices["firstaid"])
		#logging.debug("Price of lowlight for %s: %d", school.id, prices["night"])
		#logging.debug("Price of MC intro for %s: %d", school.id, prices["mc_intro"])
		#logging.debug("Price of moped intro for  %s: %d", school.id, prices["moped_intro"])
		logging.debug("Package price of %s: %d", school.id, tg_package_price)
		#logging.debug("Package price without discount of %s: %d", school.id, tg_pre_discount_under_25)
		#logging.debug("Discount of %s: %d", school.id, tg_discount_under_25)




def parse_xpath(xpath, tree, e_info, front=False):

	try:
		element = tree.xpath(xpath)
		if len(element) == 0:
			error_handler(0, e_info)
			return float("inf")
		element = element[0].text.lower()


	except lxml.etree.XPathEvalError as e:
		error_handler(0, e_info)
		return float("inf")

	element = re.sub(r"(?<=\d) (?=\d)|(^[^\d]+|(?<=\d)[^\d]+$)", '', element).split("+")
	prices = []
	for el in element:
		el = re.sub(r"\D+$", '', el)

		if front:
			el = el.split()[0]
		else:
			el = el.split()[-1]

		price = re.sub("[^0-9]", '', el)

		prices.append(int(price))

	return sum(prices)






def format_url(url):
    if not re.match("(?:http|https)://", url):
        return f"http://{url}"
    return url

def error_handler(e, e_info):
	errors = [	"Scraping Error. XPath does not exist in the HTML document.",
				"Numerical Error. The XPath points to a string, not a number.",
				"Timeout Error. The scraping thread timed out in an attempt to load or scrape the page. Page could be down.",
				"Error. Traceback provided."]
	if len(e_info) == 2:
		logging.debug("Error message %d at %s for XPath in %s.", e, e_info[0], e_info[1])
		logging.debug(errors[e])
	elif len(e_info) == 1:
		logging.debug("Error message %d at %s.", e, e_info)
		logging.debug(errors[e])
	else:
		logging.debug("Python error. %s",  errors[e])
	return


if __name__ == '__main__':
	Main()