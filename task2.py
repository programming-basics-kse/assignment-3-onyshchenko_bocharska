import argparse
from pyexpat.errors import messages

parser = argparse.ArgumentParser("Analyze Olympic medal data.")

parser.add_argument("data_file", help="Path to the TSV data file")

parser.add_argument("-output",
                    type = str,
                    help = "Filepath for your results")

parser.add_argument("-medals",
                    nargs = 2,                      # тут для змінної medals вказуємо кількість аргументів яку вона після себе приймає (тут 2)
                    metavar = ("country", "year"),  # тут вказуємо назви цих аргументів
                    help = "Input: country and year. Output: names of 10 medalists.") # потім коли треба якийсь аргумент, просто пишемо args.medals[index], для country індекс 0, для year індекс 1

parser.add_argument("-total",
                    nargs = 1,
                    metavar = "year")

parser.add_argument("-overall",
                    nargs = "+",
                    metavar = "country",
                    help = "Pick at least one country")

args = parser.parse_args()

def get_data(file_name):
    countries_dict = {}
    with open(file_name, "r") as datafile:
        next(datafile)
        for line in datafile:
            athlete = make_athlete(line)
            if athlete["medal"] == "NA":
                continue
            if athlete["country"] not in countries_dict:
                countries_dict[athlete["country"]] = {}
            if athlete["year"] not in countries_dict[athlete["country"]]:
                countries_dict[athlete["country"]][athlete["year"]] = {}
            if athlete["medal"] not in countries_dict[athlete["country"]][athlete["year"]]:
                countries_dict[athlete["country"]][athlete["year"]][athlete["medal"]] = 0
            if "total" not in countries_dict[athlete["country"]][athlete["year"]]:
                countries_dict[athlete["country"]][athlete["year"]]["total"] = 0
            countries_dict[athlete["country"]][athlete["year"]][athlete["medal"]] += 1
            countries_dict[athlete["country"]][athlete["year"]]["total"] += 1
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
    return max, best_year

def print_result(result_dict, country_name):
    message = f"{country_name}'s best result was in {result_dict[country_name][1]} with a total of {result_dict[country_name][0]} medals"
    return message

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
    return (args.medals[0] == athlete["team"] or args.medals[0] == athlete["noc"]) and args.medals[1] == athlete["year"] and athlete["medal"] != "NA" # отут як я вище писав args.medals[0]

if args.medals:         # тут я додав умову щоб код виконувався лише якщо вписали -medals
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
    totals = {}
    for country in args.overall:
        total = find_max(countries, country)
        totals[country] = total
        text = print_result(totals, country)
        if args.output:
            with open(args.output, "a") as file:
                file.write(text + "\n")



