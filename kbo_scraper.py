from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import requests

from LinkScrapper import LinkScrapper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
os.chdir("D:/sandeep")
links_scrapper = LinkScrapper()

# load saved links
links_scrapper.load_game_links()
game_links = links_scrapper.game_links
print(len(game_links),'game links loaded')

def convert_float(z):
    if len(z.split()) > 1:
        z_num, z_frac = z.split()
        if '⅔' in z_frac:
            return float(z_num)+.66
        else :
            return float(z_num)+.33
    else :
        return float(z)

def get_game_data(game_link):
    browser = webdriver.Chrome()
    browser.get(game_link)
    html = browser.page_source

    soup = BeautifulSoup(html, 'lxml')
    try:
        date_str = soup.find(id="content-container").find('time').attrs.get('datetime')
        date_obj = datetime.datetime.strptime(date_str, f'%Y-%m-%dT%H:%M:%SZ')
        date_str = date_obj.strftime(f'%d/%m/%y %I:%M%p')
    except:
        date_obj = datetime.datetime.strptime(game_link.split('-')[-1], '%Y%m%d')
        date_str = date_obj.strftime(f'%d/%m/%y')
    status = soup.find(id="scoreboard-and-links").text.__str__().replace('\n',' ').strip().lower()
    if 'canceled' in status:
        return None
    
    home_team_name = soup.find(id="scoreboard-container").find(class_='scoreboard').find_all(class_="team-name")[1].text.strip()
    away_team_name = soup.find(id="scoreboard-container").find(class_='scoreboard').find_all(class_="team-name")[0].text.strip()

    records_df = pd.read_html(soup.find(id='content-container').find(class_='records').prettify())[0]
    
    try:
        stadium = records_df[records_df[0] == 'Venue'].values[0][1]
    except:
        stadium = 'Not given'
    
    try:
        attendance = records_df[records_df[0] == 'Attendance'].values[0][1]
    except:
        attendance = 'Not given'
    
    runs_elems = soup.find(id="scoreboard-container").find(class_="scoreboard").find_all(class_="runs")

    home_score = runs_elems[1].text.strip()
    home_hits = eval(f'runs_elems[1]{".nextSibling"*1 *2}.text.strip()')
    home_errors = eval(f'runs_elems[1]{".nextSibling"*2*2}.text.strip()')

    away_score = runs_elems[0].text.strip()
    away_hits = eval(f'runs_elems[0]{".nextSibling"*1 *2}.text.strip()')
    away_errors = eval(f'runs_elems[0]{".nextSibling"*2*2}.text.strip()')


    away_df = pd.read_html(soup.find(id='live-batters').find('table',class_='away').prettify())[0]
    home_df = pd.read_html(soup.find(id='live-batters').find('table',class_='home').prettify())[0]

    away_ab  = away_df.AB.sum()
    away_rbi = away_df.RBI.sum()
    away_bb  = away_df.BB.sum()
    away_hr  = away_df.HR.sum()
    away_hbp = away_df.HBP.sum()
    away_so  = away_df.SO.sum()


    home_ab  = home_df.AB.sum()
    home_rbi = home_df.RBI.sum()
    home_bb  = home_df.BB.sum()
    home_hr  = home_df.HR.sum()
    home_hbp = home_df.HBP.sum()
    home_so  = home_df.SO.sum()

    away_pitching_df = pd.read_html(soup.find(id='live-pitchers').find('table',class_='away').prettify())[0]
    home_pitching_df = pd.read_html(soup.find(id='live-pitchers').find('table',class_='home').prettify())[0]

    for col in ['IP', 'NP', 'H', 'BB', 'HB', 'SO', 'ER', 'GS']:
        away_pitching_df[col] = away_pitching_df[col].apply(lambda z: float(z) if isinstance(z, int) or isinstance(z, float) else convert_float(z))
        home_pitching_df[col] = home_pitching_df[col].apply(lambda z: float(z) if isinstance(z, int) or isinstance(z, float) else convert_float(z))

    away_sp_name = ' '.join(away_pitching_df.loc[0][0].split()[:-1])
    home_sp_name = ' '.join(home_pitching_df.loc[0][0].split()[:-1])

    away_line_0 = away_pitching_df.loc[0]
    away_sp_ip = away_line_0['IP']
    away_sp_np = away_line_0['NP']
    away_sp_h  = away_line_0['H']
    away_sp_bb = away_line_0['BB']
    away_sp_hb = away_line_0['HB']
    away_sp_so = away_line_0['SO']
    away_sp_er = away_line_0['ER']
    away_sp_gs = away_line_0['GS']

    away_rest_lines_sum = away_pitching_df[1:].sum()
    away_bp_ip = away_rest_lines_sum['IP']
    away_bp_np = away_rest_lines_sum['NP']
    away_bp_h  = away_rest_lines_sum['H']
    away_bp_bb = away_rest_lines_sum['BB']
    away_bp_hb = away_rest_lines_sum['HB']
    away_bp_so = away_rest_lines_sum['SO']
    away_bp_er = away_rest_lines_sum['ER']
    away_bp_gs = away_rest_lines_sum['GS']

    home_line_0 = home_pitching_df.loc[0]
    home_sp_ip = home_line_0['IP']
    home_sp_np = home_line_0['NP']
    home_sp_h  = home_line_0['H']
    home_sp_bb = home_line_0['BB']
    home_sp_hb = home_line_0['HB']
    home_sp_so = home_line_0['SO']
    home_sp_er = home_line_0['ER']
    home_sp_gs = home_line_0['GS']

    home_pitching_df[1:]

    home_rest_lines_sum = home_pitching_df[1:].sum()
    home_bp_ip = home_rest_lines_sum['IP']
    home_bp_np = home_rest_lines_sum['NP']
    home_bp_h  = home_rest_lines_sum['H']
    home_bp_bb = home_rest_lines_sum['BB']
    home_bp_hb = home_rest_lines_sum['HB']
    home_bp_so = home_rest_lines_sum['SO']
    home_bp_er = home_rest_lines_sum['ER']
    home_bp_gs = home_rest_lines_sum['GS']

    output = [  date_str,
                game_link,
                
                home_team_name,
                away_team_name,
                
                stadium,
                attendance,
                
                home_score,
                away_score,
                home_hits,
                away_hits,
                home_errors,
                away_errors,
                    
                away_ab,
                away_rbi,
                away_bb,
                away_hr,
                away_hbp,
                away_so,

                home_ab,
                home_rbi,
                home_bb,
                home_hr,
                away_hbp,
                home_so,
                
                away_sp_name,
                away_sp_ip,
                away_sp_np,
                away_sp_h ,
                away_sp_bb,
                away_sp_hb,
                away_sp_so,
                away_sp_er,
                away_sp_gs,

                away_bp_ip,
                away_bp_np,
                away_bp_h ,
                away_bp_bb,
                away_bp_hb,
                away_bp_so,
                away_bp_er,


                home_sp_name,
                home_sp_ip,
                home_sp_np,
                home_sp_h ,
                home_sp_bb,
                home_sp_hb,
                home_sp_so,
                home_sp_er,
                home_sp_gs,

                home_bp_ip,
                home_bp_np,
                home_bp_h ,
                home_bp_bb,
                home_bp_hb,
                home_bp_so,
                home_bp_er,
            ]
    return output
    
    
game_data_file = input('Enter game data file location, default="game_data_file.csv":') or r'game_data_file.csv'

with open(game_data_file,'w+',encoding = "utf-8") as f:
    f.write('Date,url,Home Team,Away Team,Stadium,Attendance,Home Score,Away Score,Home Hits,Away Hits,Home Errors,Away Errors,Away AB,Away RBI,Away BB,Away HR,Away HBP,Away SO,Home AB,Home RBI,Home BB,Home HR,Home HBP,Home SO,Away SP Name,Away SP IP,Away SP NP,Away SP H,Away SP BB,Away SP HB,Away SP SO,Away SP ER,Away SP GS,Away BP IP,Away BP NP,Away BP H,Away BP BB,Away BP HB,Away BP SO,Away BP ER,Home SP Name,Home SP IP,Home SP NP,Home SP H,Home SP BB,Home SP HB,Home SP SO,Home SP ER,Home SP GS,Home BP IP,Home BP NP,Home BP H,Home BP BB,Home BP HB,Home BP SO,Home BP ER\n')

failed_urls = []
for game_link in tqdm(game_links):
    try:
        game_data = get_game_data(game_link)
        if not game_data:
            continue
        with open(game_data_file,'a',encoding="utf-8") as f:
            f.write(','.join(str(data).__repr__().replace("'",'"') if ',' in str(data) else str(data) for data in game_data)+'\n')
    except Exception as e:
        print(game_link)
        print(e)
        failed_urls.append(game_link)



failed_urls_file_path = f'failed_links.txt'
with open(failed_urls_file_path, 'w+',encoding="utf-8") as failed_link_file:
    failed_link_file.write('\n'.join( map(lambda f: ','.join(f), failed_urls) ))
print('Failed links:')
print('\n'.join(failed_urls))
