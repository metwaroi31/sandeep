from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


import os
os.chdir("D:/sandeep")
class LinkScrapper():
    def __init__(self,year=2021,month=1,date=1, current_year=2021,current_month=6,current_date=1):
        self.game_links = []
        self.start_date   = datetime.datetime(year        , month        , date        )
        self.current_date = datetime.datetime(current_year, current_month, current_date)
        self.year = year

    def get_game_links(self):
        current_date = self.current_date or datetime.datetime.now()
        week_delta = datetime.timedelta(days=7)
        weekly_links = []
        for i in range((self.current_date - self.start_date).days):
            weekdate = self.start_date + i * week_delta
            if weekdate > self.current_date:
                break
            weekdate = weekdate.strftime('%Y-%m-%d')
            weekly_url = fr'https://mykbostats.com/schedule/week_of/{weekdate}'
            options = Options()
            options.headless = True

            try:
                browser = webdriver.Chrome()
                browser.get(weekly_url)
                html = browser.page_source
                weekly_games_soup = BeautifulSoup(html, 'lxml')
            except Exception as e:
                print(weekdate)
                print(e)
                weekly_games_soup = BeautifulSoup('', 'lxml')
            weekly_a_elems = weekly_games_soup.find_all(class_='game-line')
            if not weekly_a_elems:
                print(weekdate,'does not have any game links.')
                continue
            base_link = r'https://mykbostats.com'
            for a_elem in weekly_a_elems:
                if a_elem.find(class_='inning'):
                    link = base_link+a_elem.attrs.get('href','')
                    print (link)
                    weekly_links.append(link)
                    if link == base_link:
                        continue
            pass
        
        weekly_links = list(set(weekly_links))
        self.game_links.extend(weekly_links)
        
    def load_game_links(self,links_file_path=''):
        file_path = links_file_path or f'game_links.txt'
        with open(file_path, 'r') as game_link_file:
            game_links = list(map(lambda link: link[:-1], game_link_file.readlines()))
        self.game_links = list(filter(lambda z:z,game_links))

    def save_game_links(self,links_file_path=''):
        file_path = links_file_path or f'game_links.txt'
        with open(file_path, 'w+') as game_link_file:
            game_link_file.write('\n'.join(self.game_links))
            game_link_file.write('\n')
            
if __name__ == '__main__':
    start_date = input('Start date in format yyyy-mm-dd :') or '2022-02-01'
    end_date   = input('End date in format yyyy-mm-dd :') or '2022-12-01'
    start_date = list(map(int,start_date.split("-")))
    end_date   = list(map(int,end_date.split("-")))
    
    links_file_path = input('Enter links file path, default="game_links.txt" :') or "game_links.txt"
    
    links_scrapper = LinkScrapper(  year          = start_date[0] ,
                                    month         = start_date[1] ,
                                    date          = start_date[2] , 
         
                                    current_year  = end_date[0] ,
                                    current_month = end_date[1] ,
                                    current_date  = end_date[2] )

    # save new game links
    links_scrapper.get_game_links()
    links_scrapper.save_game_links(links_file_path)
    print(len(links_scrapper.game_links),'links saved')

