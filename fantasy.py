# This gets the ESPN fantasy football projections for the 2016 season by week
# Usage: $ python fantasy.py {week}

import pandas as pd
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime, date
from collections import defaultdict
from enum import Enum

YEAR = "2016"

ACTUAL_PTS_URL = "http://games.espn.com/ffl/leaders?&scoringPeriodId={0}&seasonId=" + YEAR + "{1}&slotCategoryId={2}"
PREDICTED_PTS_URL = "http://games.espn.go.com/ffl/tools/projections?&leagueId=0&scoringPeriodId={0}&seasonId=" + YEAR + "{1}"

# The value ESPN gives the position in the URL
class Position(Enum):
    QB = 0
    RB = 2
    WR = 4
    TE = 6
    DST = 16
    K = 17

# Gets the fantasy point total
# Returns a dict indexed by player with values of points and his position
def get_actual(number):
    print("Getting actual points...")
    pages = ["&startIndex=0", "&startIndex=50", "&startIndex=100"] 
    position = [Position.QB.value, Position.RB.value, Position.WR.value, Position.TE.value, Position.DST.value, Position.K.value]

    result = defaultdict(dict)

    for pos in position:
        for page in pages:
            r = requests.get(ACTUAL_PTS_URL.format(number, page, pos))
            bs = BeautifulSoup(r.text)
            table = bs.findAll('table')[0]
            rows = table.findAll(['tr'])

            if pos == Position.QB.value:
                player_pos = "QB"
            elif pos == Position.RB.value:
                player_pos = "RB"
            elif pos == Position.WR.value:
                player_pos = "WR"
            elif pos == Position.TE.value:
                player_pos = "TE"
            elif pos == Position.DST.value:
                player_pos = "DST"
            elif pos == Position.K.value:
                player_pos = "K"

            for row in rows[3:]:
                try:
                    name = row.findAll(['td'])[0].a.string
                    points = float(row.findAll(['td'])[23].string)
                    result[name] = points, player_pos
                except IndexError:
                    pass
    return result

# Returns a dict of the player and their projected points
def get_projected(number):
    print("Getting projections...")
    pages = ["", "&startIndex=40", "&startIndex=80", "&startIndex=120", "&startIndex=160", "&startIndex=200", "&startIndex=240"] 

    result = defaultdict(dict)

    for page in pages:
        r = requests.get(PREDICTED_PTS_URL.format(number, page))
        bs = BeautifulSoup(r.text)

        tables = bs.findAll('table')
        table = tables[0]
        rows = table.findAll(['tr'])

        for row in rows[2:]:
            points = row.findAll(['td'])
            names = row.a.string
            for point in points:
                try:
                    value = float(point.string)
                except (TypeError, ValueError) as e:
                    value = 0.0 
                result[names] = value 
    return result

# Writes the projected and predicted to a dataframe
def get_dataframe(result1, result2):
    print("Writing dataframe...")
    df1 = pd.DataFrame.from_dict(result1, orient='index')
    df2 = pd.DataFrame.from_dict(result2, orient='index')
    df = pd.concat([df1,df2], axis=1)
    df.index.name = 'names'
    df.columns = ['projected', 'actual','position']

    return df

def make_csv(df, week):
    df.to_csv("data/fantasy_wk" + week + ".csv")

def main(week):
    projected = get_projected(week)
    actual = get_actual(week)
    df = get_dataframe(projected, actual)
    make_csv(df, week)
    print("Done!")

if __name__ == '__main__':
    try:
        if 1 <= int(sys.argv[1]) <= 16:
            main(sys.argv[1])
        else:
            raise ValueError("Enter a week between 1 and 16")
    except IndexError as e:
        print("Not enough arguments") 
