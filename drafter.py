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

def get_single_player_projection(url, stat_names, projection_db):
    """ If the URL exists, turn the player's projections into a dict and add the
        dict to the projection DB """
    try:
        # Attempt to retrieve the page and turn it into soup
        response = request.urlopen(url)
        soup = bs(response, features="lxml")

        # Extract player's name from the soup
        player_name = soup.find('h1').string

        # Extra player's position
        if soup.find('div', class_='player-info-box-pos').string == 'P':
            position = 1
        else:
            position = 0

        # Extract all of the projections from the soup
        player_stats = []
        for i in 1,2:
            player_stats_temp = []
            stat_table = soup.find('table', id=re.compile("SeasonStats1_dgSeason{}_ctl00".format(i)))
            stat_rows = stat_table.find_all('tr', class_=re.compile("grid_projections_show"))
            for stat_row in stat_rows:
                stats_list = [cell.string for cell in stat_row.find_all('td')]
                player_stats_temp.append(stats_list)
            player_stats.append(player_stats_temp)

        # Put all of the stats into a dict and then add the dict to the
        # projeciton db
        player_stats_dict = {}
        for i in range(2):
            for stat_row in player_stats[i]:
                player_stats_dict.setdefault(stat_row[1], {})
                for j in range(2, len(stat_names[position][i])):
                    player_stats_dict[stat_row[1]])[stat_names[position][i][j]] = stat_row[j]

        if player_stats_dict:
            projection_db[player_name] = player_stats_dict
            print("Added {}".format(player_name))

    except urllib.error.HTTPError:
        return
            

def get_stat_names(url):
    """ Create a list with field names for use in creating dicts later """
    # Grab the page from Fangraphs from which to take the stat names and parse
    # out the relevant two tables ("Standard" and "Advanced" on the player page)
    response = request.urlopen(url)
    soup = bs(response, features="lxml")
    stat_tables = soup.find_all('table', id=re.compile("SeasonStats1_dgSeason[12]_ctl00"))
    # Take all of the table headers and put them into two lists
    stat_names = []
    for stat_table in stat_tables[0], stat_tables[1]:
        stat_names_subset = []
        stat_names_subset.extend(cell.string for cell in stat_table.find_all('th'))
        stat_names.append(stat_names_subset) 
    return stat_names

def get_fangraphs_projections():
    # If behind Intel proxy server, set up proxy support
    try:
        requests.get("http://www.google.com")
    except requests.exceptions.ProxyError:
        setup_intel_proxy()
    
    # Set the generic part of the URL to request for each player
    url_prefix = "https://www.fangraphs.com/statss.aspx?playerid="
    batter_stats_url = "https://www.fangraphs.com/statss.aspx?playerid=1"
    pitcher_stats_url = "https://www.fangraphs.com/statss.aspx?playerid=18"
    # Get a list of stat names
    batter_stat_names = get_stat_names(batter_stats_url)
    pitcher_stat_names = get_stat_names(pitcher_stats_url)
    stat_names = [batter_stat_names,pitcher_stat_names]
    # Retrieve all of the available data for each player
    projection_db = {}
    for i in range(15490,15510):
        url = "{}{}".format(url_prefix,i)
        get_single_player_projection(url, stat_names, projection_db)
        time.sleep(10)

    return projection_db

if __name__ == "__main__":
    get_fangraphs_projections()