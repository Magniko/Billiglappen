import os
import pandas as pd 

schools_tuple = (
				"fortraas1989",
				"haltraav3521",
				"kontraav4202",
				"learbekk5038",
				"lechtraf2624",
				"oslbaetu8831",
				"vesbaetr0190"
)
columns_class = (
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


schools = pd.read_csv("filtered_driving_schools.csv")
basic_course = pd.read_csv("tg_driving_schools.csv")


for school in schools_tuple:
	file_name = f"light_classes_xpaths/{school}_light_classes.csv"

	if not os.path.exists(file_name):
		row = schools[schools["id"] == school]
		dict_ = {
			"id": row["id"].item(),
			"name": row["name"].item(),
			"website": row["website"].item(),
		}

		class_ = pd.DataFrame(dict_, columns=columns_class, index=[0])
		basic_course = basic_course.append(dict_, ignore_index=True)
		class_.to_csv(file_name, index=None)

basic_course.to_csv("tg_driving_schools.csv", index=None)
