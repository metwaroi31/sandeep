from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import re
from difflib import SequenceMatcher

import undetected_chromedriver as uc
from twilio.rest import Client
from datetime import datetime, timedelta

import time
import requests
import os
import xlrd

TWILIO_NUMBER = "CONSTANT"
TWILIO_SID = "CONSTANT"
TWILIO_TOKEN = "CONSTANT"


ACCOUNT_SID = TWILIO_SID
AUTH_TOKEN = TWILIO_TOKEN
client = Client(ACCOUNT_SID, AUTH_TOKEN)


def suppress_exception_in_del(uc):
    old_del = uc.Chrome.__del__

    def new_del(self) -> None:
        try:
            old_del(self)
        except:
            pass

    setattr(uc.Chrome, "__del__", new_del)


def get_yesterday():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    return yesterday.strftime("%d/%m")


class automater:
    def __init__(self, username, password):
        current_directory = os.getcwd()

        self.username = username
        self.password = password
        self.staff = []

        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "prefs", {"download.default_directory": current_directory}
        )
        options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.get("https://zoobi-rz.retailzoo.com.au/pentaho/boost/reports.html")

    def login(self):
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='j_username']"))
        ).send_keys(self.username)

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='j_password']"))
        ).send_keys(self.password)

        self.driver.find_element(By.XPATH, "//input[@id='pentaho_submit']").click()

    def desktop(self):
        iframe_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        self.driver.switch_to.frame(iframe_element)

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Document Listing')]")
            )
        ).click()

    def document_listing(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.switch_to.default_content()
        iframe1 = WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        self.driver.switch_to.frame(iframe1)

        iframe2 = WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        self.driver.switch_to.frame(iframe2)

        iframe3 = WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.ID, "reportContent"))
        )
        self.driver.switch_to.frame(iframe3)

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Sales Person Summary')]")
            )
        ).click()

    def generate_excel(self):
        # time.sleep(10)
        # self.driver.get("https://zoobi-rz.retailzoo.com.au/pentaho/mobileviewer/index.html?solution=Boost&path=%2F6.+Sales+Person&name=Sales+Person+Summary.prpt")
        self.driver.switch_to.window(self.driver.window_handles[2])
        self.driver.switch_to.default_content()

        iframe1 = WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        self.driver.switch_to.frame(iframe1)

        select_elms = WebDriverWait(self.driver, 40).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )
        select_element_yesterday = Select(select_elms[0])
        select_element_yesterday.select_by_visible_text("Yesterday")

        select_element_yesterday = Select(select_elms[-1])
        select_element_yesterday.select_by_visible_text("Excel")

        file_name = "Sales Person Summary.xls"

        if os.path.exists(file_name):
            os.remove(file_name)

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'View Report')]")
            )
        ).click()

    def get_data(self):
        url = "https://my.tanda.co/api/v2/users"

        headers = {
            "Authorization": "Bearer {{CONSTANT}}"
        }
        response = requests.request("GET", url, headers=headers)

        cockburn_gateway = response.json()
        name_phones_1 = []
        for s in cockburn_gateway:
            name_phones_1.append({"name": s["name"], "phone": s["normalised_phone"]})
        headers = {
            "Authorization": "Bearer {{CONSTANT}}"
        }

        response = requests.request("GET", url, headers=headers)

        juice_carousel = response.json()
        name_phones_2 = []
        for s in juice_carousel:
            name_phones_2.append({"name": s["name"], "phone": s["normalised_phone"]})

        workbook = xlrd.open_workbook("./Sales Person Summary.xls")
        sheet = workbook.sheet_by_index(0)

        column_b_index = 1
        column_v_index = 21
        column_e_index = 4
        column_u_index = 20

        for row in range(6, sheet.nrows):
            b_value = sheet.cell_value(row, column_b_index)
            v_value = sheet.cell_value(row, column_v_index)
            e_value = sheet.cell_value(row, column_e_index)
            u_value = sheet.cell_value(row, column_u_index)

            if b_value and isinstance(v_value, (int, float)):
                data_dict = {
                    "name": b_value,
                    "phone": None,
                    "vibe%trans": v_value * 100,
                    "sales_trans": e_value,
                    "vibe_trans": u_value,
                }
                self.staff.append(data_dict)

        def similar_enough(str1, str2, threshold=0.9):
            return SequenceMatcher(None, str1, str2).ratio() > threshold

        def are_names_similar(name_1, name_2):
            words_1 = name_1.split()
            words_2 = name_2.split()

            if len(words_1) < 2 or len(words_2) < 2:
                return False

            return words_1[0] == words_2[0] and words_1[-1] == words_2[-1]

        def remove_id(s):
            pattern = r"\(ID:\s*\d+\)"
            return re.sub(pattern, "", s).strip()
        for employee in self.staff:
            for temp in name_phones_1:
                name_1 = remove_id(employee["name"])
                name_2 = temp["name"]

                if similar_enough(name_1, name_2) or are_names_similar(name_1, name_2):
                    employee["phone"] = temp["phone"]
                    employee['manager'] = "gateway"
                
            for temp in name_phones_2:
                name_1 = remove_id(employee["name"])
                name_2 = temp["name"]

                if (
                    similar_enough(name_1, name_2) or are_names_similar(name_1, name_2)
                ) and employee["phone"] == None:
                    employee["phone"] = temp["phone"]
                    employee['manager'] = 'carousel'

        return self.staff

    def get_final_data(self):
        data = user.get_data()

        success_count = 0
        not_successful_count = 0
        successful_people = []
        successful_gateway_people = []
        successful_carousel_people = []

        carousel_total_vibe = 0
        gateways_total_vibe = 0

        for d in data:
            print (d)
            if d["name"] == "Carousel Total:":
                carousel_total_vibe = round(d["vibe%trans"], 1)
                continue

            if d["name"] == "Gateways Total:":
                gateways_total_vibe = round(d["vibe%trans"], 1)
                continue

            if (
                d["name"] == "Polygon Online Ordering (ID: -100)"
                or d["name"] == "Uber Eats  Online Ordering (ID: -102)"
                or d["name"] == "DoorDash Online Ordering (ID: -108)"
                or d["name"] == "Polygon Online Ordering (ID: -100)"
                or d["name"] == "Total:"
                or "Menulog" in d["name"]
            ):
                continue
            vibe_percent = round(d["vibe%trans"], 1)
                
            if d["phone"] != None:
                sales_trans = (
                    int(d["sales_trans"])
                    if d["sales_trans"] == int(d["sales_trans"])
                    else d["sales_trans"]
                )
                vibe_trans = (
                    int(d["vibe_trans"])
                    if d["vibe_trans"] == int(d["vibe_trans"])
                    else d["vibe_trans"]
                )

                vibe_percent = round(d["vibe%trans"], 1)

                body = f"Hi {d['name']} . Yesterday ({get_yesterday()}) you served {sales_trans} customers, of which {vibe_trans} had a vibe swipe. Your % was {vibe_percent}"

                # client.messages.create(to=d["phone"], from_=TWILIO_NUMBER, body=body)
                if d["manager"] == "gateway":
                    successful_gateway_people.append(
                        {"name": d["name"], "vibe": vibe_percent, "status": "SMS Sent"}
                    )
                else :
                    successful_carousel_people.append(
                        {"name": d["name"], "vibe": vibe_percent, "status": "SMS Sent"}
                    )

                successful_people.append(
                    {"name": d["name"], "vibe": vibe_percent, "status": "SMS Sent"}
                )
                success_count += 1
            else:
                successful_people.append(
                    {"name": d["name"], "vibe": vibe_percent, "status": "SMS Not Sent"}
                )
                not_successful_count += 1

        results_summary = (
            f"SUCESSFUL: {success_count}\nUNSUCCESSFUL: {not_successful_count}"
        )
        carousel_summary = f"Carousel Total: {carousel_total_vibe}%"
        gateways_summary = f"Gateway Total: {gateways_total_vibe}%"
        
        gateways_members = (
            "\n".join(
                [
                    f"{person['name']} / {person['vibe']}%: {person['status']}"
                    for person in successful_gateway_people
                ]
            )
        )
        carousel_members = (
            "\n".join(
                [
                    f"{person['name']} / {person['vibe']}%: {person['status']}"
                    for person in successful_carousel_people
                ]
            )
        )

        results = (
            results_summary
            + "\n\n"
            + carousel_summary
            + "\n"
            + gateways_summary
            + "\n\n"
            + "\n\n".join(
                [
                    f"{person['name']} / {person['vibe']}%: {person['status']}"
                    for person in successful_people
                ]
            )
        )

        return results, carousel_summary, gateways_summary, carousel_members, gateways_members

    def send_extra_messages(self, results, carousel_average, carousel_members, gateway_avarage, gateway_members):
        client.messages.create(to="+61412812760", from_=TWILIO_NUMBER, body=results)
        print (results)
        print (carousel_average)
        print (carousel_members)
        print (gateway_avarage)
        print (gateway_members)
        
        carousel_avg_message = f"CAROUSEL AVERAGE: {carousel_average}%"
        gateway_avg_message = f"CAROUSEL AVERAGE: {gateway_avarage}%"
        
        print(client.messages.create(
            to="+61432402483", from_=TWILIO_NUMBER, body=carousel_avg_message
        ))
        print(client.messages.create(
            to="+61452355052", from_=TWILIO_NUMBER, body=gateway_avg_message
        ))

        print(client.messages.create(
            to="+61432402483", from_=TWILIO_NUMBER, body=carousel_members
        ))
        print(client.messages.create(
            to="+61452355052", from_=TWILIO_NUMBER, body=gateway_members
        ))




if __name__ == "__main__":
    user = automater("gat1", "zoobigat1")
    user.login()
    user.desktop()
    user.document_listing()
    user.generate_excel()
    time.sleep(60)

    results, carousel_average, gateway_average, carousel_members, gateways_members = user.get_final_data()
    user.send_extra_messages(results, carousel_average, carousel_members, gateway_average, gateways_members)

    # suppress_exception_in_del(uc)
