import argparse
from pyexpat.errors import messages

parser = argparse.ArgumentParser("Analyze Olympic medal data.")

parser.add_argument("data_file", help="Path to the TSV data file")

parser.add_argument("-output",
                    type = str,
                    help = "Filepath for your results")

parser.add_argument("-medals",
                    nargs = 2,
                    metavar = ("country", "year"),
                    help = "Input: country and year. Output: names of 10 medalists.")

parser.add_argument("-total",
                    nargs = 1,
                    metavar = "year")

parser.add_argument("-overall",
                    nargs = "+",
                    metavar = "country",
                    help = "Pick at least one country")

parser.add_argument("-interactive",
                    action = "store_true",
                    help = "Starts an interacrive mode.")

args = parser.parse_args()

def get_data(file_name):
    countries_dict = {}
    with open(file_name, "r") as datafile:
        next(datafile)
        for line in datafile:
            athlete = make_athlete(line)
            if athlete["team"] not in countries_dict:
                countries_dict[athlete["team"]] = {}
            if athlete["year"] not in countries_dict[athlete["team"]]:
                countries_dict[athlete["team"]][athlete["year"]] = {}
                countries_dict[athlete["team"]][athlete["year"]]["city"] = athlete["city"]
            if "total" not in countries_dict[athlete["team"]][athlete["year"]]:
                countries_dict[athlete["team"]][athlete["year"]]["total"] = 0
            if athlete["medal"] == "NA":
                continue
            if athlete["medal"] not in countries_dict[athlete["team"]][athlete["year"]]:
                countries_dict[athlete["team"]][athlete["year"]][athlete["medal"]] = 0

            countries_dict[athlete["team"]][athlete["year"]][athlete["medal"]] += 1
            countries_dict[athlete["team"]][athlete["year"]]["total"] += 1
        return countries_dict


def find_max(country_list, country_name):
    years = country_list[country_name].keys()
    max = 0
    best_year = ""
    for year in years:
        max_check = country_list[country_name][year]["total"]
        if max_check > max:
            max = max_check
            best_year = year
    message = f"{country_name}'s best result was in {best_year} with a total of {max} medals"
    return message

def find_min(country_list, country_name):
    years = country_list[country_name].keys()
    min = 100000
    best_year = ""
    for year in years:
        min_check = country_list[country_name][year]["total"]
        if min_check < min:
            min = min_check
            worst_year = year
    message = f"{country_name}'s worst result was in {worst_year} with a total of {min} medals"
    return message

def find_mean(dictionary):
    n_of_yrs = 0
    tot_g = 0
    tot_s = 0
    tot_b = 0
    for year in dictionary.values():
        n_of_yrs += 1
        tot_g += year.get("Gold", 0)
        tot_s += year.get("Silver", 0)
        tot_b += year.get("Bronze", 0)
    return f"The team gets: {round(tot_g/n_of_yrs, 2)}-golden, {round(tot_s/n_of_yrs, 2)}-silver, {round(tot_b/n_of_yrs, 2)}-bronze medals, on average."

def make_athlete(line):
    [id, name, sex, age, height, weight, team, noc, games, year, season, city, sport, event, medal] = line.split('\t')
    return {
        "id": id,
        "name": name,
        "sex": sex,
        "age": age,
        "height": height,
        "weight": weight,
        "team": team,
        "noc": noc,
        "games": games,
        "year": int(year),
        "season": season,
        "city": city,
        "sport": sport,
        "event": event,
        "medal": medal.strip(),
    }

def is_good(line):
    athlete = make_athlete(line)
    return (args.medals[0] == athlete["team"] or args.medals[0] == athlete["noc"]) and args.medals[1] == athlete["year"] and athlete["medal"] != "NA"

if args.medals:
    with open(args.data_file) as file:
        medals = {"gold": 0, "silver": 0, "bronze": 0}

        next(file)
        athletes = [make_athlete(line) for line in file if is_good(line)]

        for idx, athlete in enumerate(athletes):
            if idx < 10:
                print(f"{athlete["name"]} - {athlete["sport"]} - {athlete["medal"]}")

            if athlete["medal"] == "Gold":
                medals["gold"] +=1
            elif athlete["medal"] == "Silver":
                medals["silver"] +=1
            else:
                medals["bronze"] +=1
        print(medals)

if args.total:
    with open(args.data_file) as file:
        next(file)
        teams = {}
        for line in file:
            line = make_athlete(line)
            if str(line["year"]) == args.total[0] and line["medal"] != "NA":
                if line["team"] in teams:
                    teams[line["team"]][line["medal"]] += 1 #мені за це соромно
                else:
                    teams[line["team"]] = {"Gold": 0, "Silver": 0, "Bronze": 0}
                    teams[line["team"]][line["medal"]] += 1
    for team in teams:
        text = f"{team} - Gold:{teams[team]['Gold']} - Silver:{teams[team]['Silver']} - Bronze:{teams[team]['Bronze']}"
        print(text)
        if args.output:
            with open(args.output, "a") as file:
                file.write(text + "\n")

if args.overall:
    countries = get_data(args.data_file)
    for country in args.overall:
        text = find_max(countries, country)
        print(text)
        if args.output:
            with open(args.output, "a") as file:
                file.write(text + "\n")

if args.interactive: #перша участь(рік місце) | найуспішніша олімпіада(ккість медалей) | найневдаліша | середня ккість медалей кожного типу
    print("In this mode you will enter a name of a country and get a short summary of its results.")
    countries = get_data(args.data_file)

    while True:
        country = input("Please enter the name of the country, or 'exit' if you want to exit: ").strip().lower().title()
        if country == "Exit":
            exit()
        elif country in countries.keys():
            text = (f"The first year when {country} participated in Olympics was {min(countries[country].keys())} \n"    #, in {countries[country]["city"]} 
                    f"{find_max(countries, country)} \n"
                    f"{find_min(countries, country)} \n"
                    f"{find_mean(countries[country])} \n")
            print(text)
            if args.output:
                with open(args.output, "a") as file:
                    file.write(text + "\n")
        else:
            print(f"There is not such country as {country}, try again")