import pandas as pd



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
			"package_price",
			"n_lessons",
			"comment"
	)

#columns_basic = (
#			"id",
#			"name",
#			"website",
#			"price_url",
#			"theory_xpath",
#			"firstaid_xpath",
#			"night_xpath",
#			"mc_intro_xpath",
#			"moped_intro_xpath",
#			"tg_package_price"
#	)


schools = pd.read_csv("filtered_driving_schools.csv")
print(schools)

#basic_course = pd.DataFrame(columns=columns_basic)

schools_tupl = ("svesvetr4299", "wrigtraf4330")
for school in schools_tupl:
	row = schools[schools["id"] == school]
	dict_ = {"id": row["id"].item(), "name": row["name"].item(), "website": row["website"].item()}

	class_ = pd.DataFrame(dict_, columns=columns_class, index=[0])
	#basic_course = basic_course.append(dict_, ignore_index=True)
	class_.to_csv(f"light_classes_xpaths/{school}_light_classes.csv", index=None)

#basic_course.to_csv("basic_course_driving_schools_asker.csv", index=None)