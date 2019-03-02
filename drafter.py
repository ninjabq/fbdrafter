# Tool for making decisions in a fantasy baseball draft, inspired by the original
# written for the 2018 season
#
# Written by Noah Mebane
# Created: 2/26/2019
# Last Updated: 2/26/2019

import urllib.request as request
import urllib.error
import lxml.html as lhtml
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re
import time

projection_types = ['steamer']

def setup_intel_proxy():
    """ This is only required when at Intel, to navigate through the proxy """

    proxy_dict = {'http' : 'http://proxy-chain.intel.com:911', 'https' : 'http://proxy-chain.intel.com:911'}
    proxy_support = request.ProxyHandler(proxy_dict)
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)

def get_single_player_projection(url, projection_db):
    """ If the URL exists, turn the player's projections into a dict and add the
        dict to the projection DB """
    while True:
        try:
            # Attempt to retrieve the page and turn it into soup
            response = request.urlopen(url)
            soup = bs(response, features="lxml")

            player_stats_dict = {}

            # Extract player's name from the soup
            player_name = soup.find('h1').string

            # Extract player's position
            position =  soup.find('div', class_='player-info-box-pos').string

            # Extract the stat tables
            stat_tables = soup.find_all('table', id=re.compile("SeasonStats1_dgSeason[12]_ctl00"))
            stat_headers_1 = [cell.string for cell in stat_tables[0].find_all('th')]
            stat_headers_2 = [cell.string for cell in stat_tables[1].find_all('th')]
            stat_block_1 = stat_tables[0].find_all('tr', class_="grid_projections_show")
            stat_block_2 = stat_tables[1].find_all('tr', class_="grid_projections_show")
            num_projections = len(stat_block_1)

            # If this player has projections, add each projection to the DB
            if (num_projections):
                for i in range(num_projections):
                    temp_stat_dict = {"Name" : player_name, "Position" : position}
                    stat_line_1 = [cell.string for cell in stat_block_1[i].find_all('td')]
                    stat_line_2 = [cell.string for cell in stat_block_2[i].find_all('td')]
                    for j in range(len(stat_headers_1)):
                        temp_stat_dict[stat_headers_1[j]] = stat_line_1[j]
                    for j in range(len(stat_headers_2)):
                        temp_stat_dict[stat_headers_2[j]] = stat_line_2[j]
                    for stat in list(projection_db):
                        if stat in temp_stat_dict and temp_stat_dict[stat] != '\xa0':
                            projection_db[stat].append(temp_stat_dict[stat])
                        else:
                            projection_db[stat].append(" ")
        except urllib.error.HTTPError:
            return
        except urllib.error.URLError:
            sleep(10)
        else:
            break

def get_stat_names(projection_db):
    """ Set up the projection DB with the stat field names """
    
    projection_db.setdefault('Name', [])
    projection_db.setdefault('Position', [])

    # Links to a batter and a pitcher since they have different columns
    batter_stats_url = "https://www.fangraphs.com/statss.aspx?playerid=1"
    pitcher_stats_url = "https://www.fangraphs.com/statss.aspx?playerid=18"

    for url in batter_stats_url, pitcher_stats_url:
        # Grab the pages from Fangraphs from which to take the stat names and parse
        # out the relevant two tables ("Standard" and "Advanced" on the player page)
        response = request.urlopen(url)
        soup = bs(response, features="lxml")
        stat_tables = soup.find_all('table', id=re.compile("SeasonStats1_dgSeason[12]_ctl00"))
        # Create keys in the dict for each stat name
        for stat_table in stat_tables:
            for stat_name in [cell.string for cell in stat_table.find_all('th')]:
                projection_db.setdefault(stat_name, [])

def get_fangraphs_projections():
    """ Retrieve the projection data from FanGraphs, player by player """

    # If behind Intel proxy server, set up proxy support
    try:
        requests.get("http://www.google.com")
    except requests.exceptions.ProxyError:
        setup_intel_proxy()
    
    projection_db = {}
    # Generate keys for each stat name
    get_stat_names(projection_db)
    # Retrieve all of the available data for each player
    url_prefix = "https://www.fangraphs.com/statss.aspx?playerid="
    for i in [15502,11579,11493,3543]:
        url = "{}{}".format(url_prefix,i)
        get_single_player_projection(url, projection_db)
        time.sleep(10)

    df = pd.DataFrame(projection_db)
    df.to_csv(r"c:\\users\\nmebane\\desktop\\projection_db.txt")
    return projection_db

if __name__ == "__main__":
    get_fangraphs_projections()