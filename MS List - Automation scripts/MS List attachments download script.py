from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
import itertools
import time
import pandas as pd,numpy as np,os
import re,shutil
from datetime import datetime
from dateutil import parser
import urllib.parse
import webbrowser
import requests
import argparse

def extract_sharepoint_list(driver,required_id):

    list_selector = "div.odspSpartanList[data-is-scrollable='true']"
    row_selector = "div[data-automationid='list-content']"

    collected_rows = []
    seen_texts = set()

    last_height = -1

    while True:
        # Re-find list container (avoid stale element)
        list_ele = driver.find_element(By.CSS_SELECTOR, list_selector)

        # Get visible rows ONLY
        visible_rows = list_ele.find_elements(By.CSS_SELECTOR, row_selector)

        for row in visible_rows:
            try:
                id_ele_list = row.find_elements(By.CSS_SELECTOR, ".odsp-spartan-cell.field-ID-htmlGrid_1")
                text_list = [id_ele.text.strip() for id_ele in id_ele_list]
                # collected_rows+= text_list
                # collected_rows = list(np.unique(collected_rows))
            except:
                pass  # ignore stale rows

        #text_list.sort(reverse=True)
        print(text_list)
        if required_id in text_list:
            return text_list
        # Scroll down
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;", 
            list_ele
        )

        time.sleep(4)  # allow SharePoint to load next batch

        # Detect end-of-list
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight;", 
            list_ele
        )

        if new_height == last_height:
            break  # No more items to load

        last_height = new_height

    return collected_rows

def search_iteratively(driver,required_id):
    rows = extract_sharepoint_list(driver,required_id)
    return rows.index(required_id)

username = 'Nitin'

credentials_df = pd.read_csv('MS List_credentials.csv')

required_credentials_df = credentials_df[credentials_df['UserName']==username]

email = required_credentials_df['Email id'].values[0]
password = credentials_df['Password'].values[0]
full_username = credentials_df['Full UserName'].values[0]

input_csv_folderpath = input('Please enter input folderpath:')
input_csv_filename = input('Please enter csv filename containing MS ID List:')
input_csv_filepath = os.path.join(input_csv_folderpath,input_csv_filename)

output_attachments_folderpath = input('Please enter output folderpath where attachments are to be downloaded:')

df = pd.read_csv(input_csv_filepath, encoding='ISO-8859-1')

print('By default, Tickets from MS List extracted to excel file will have "ID" as default column. Kindly confirm if the input csv also has "ID" column name as MS List ID, or it has different name')
confirm_flag = input('Please confirm if "ID" is column name for MS List ID in the input file or not (case-sensitive)? (Y/N)')

if confirm_flag.lower() not in ('y','n','yes','no'):
	column_name = input('Kindly enter correct MS List ID column name (case-sensitive)')

else:
	column_name = 'ID'
	
parser = argparse.ArgumentParser(prog='MS List comments extracted script')
parser.add_argument('-i', '--index', type=int, default=-1, help="Starting MS List ID to start running the script")

args = parser.parse_args()
list_index = args.index

required_id_list = [str(item) for item in list(df[column_name].values)]
required_id_list = [item for item in required_id_list if item.isdigit()]

max_list_id = max([int(ele) for ele in required_id_list])

if list_index==-1:
    list_index = max_list_id
   
else:
    required_id_df = df[df[column_name].apply(lambda x: int(x)<=list_index)]
    required_id_list = [str(item) for item in list(required_id_df[column_name].values)]

print(len(required_id_list))

url = 'https://asterdmhealthcare57888085as.sharepoint.com/sites/AsterVCP-Internal/Lists/Aster Health Issue tracker/AllItems.aspx'
url = url.replace(' ',"%20")

driver = webdriver.Chrome()
driver.get(url)

time.sleep(2)
email_ele = driver.find_element(By.XPATH,"//input[@type='email']")
email_ele.send_keys(email)
email_ele.send_keys(Keys.ENTER)
time.sleep(2)

password_ele = driver.find_element(By.XPATH,"//input[@type='password']")
password_ele.send_keys(password)
password_ele.send_keys(Keys.ENTER)
time.sleep(2)

while(driver.current_url!=url):
    pass

print(driver.current_url)
time.sleep(2)

# id_limit=20
required_id_list_2 = required_id_list
# required_id_list_2 = required_id_list[:id_limit]
id_count=1
for required_id in required_id_list_2:
    
    searchbox_input_ele = driver.find_element(By.XPATH,"//input[contains(@class, 'searchBox')]")
    time.sleep(1)
    searchbox_input_ele.clear()
    searchbox_input_ele.send_keys(str(required_id))
    searchbox_input_ele.send_keys(Keys.ENTER)
    time.sleep(2)
    
    print('Searched for MS List ID: {}'.format(required_id))
    id_ele_list = driver.find_elements(By.CSS_SELECTOR, ".odsp-spartan-cell.field-ID-htmlGrid_1")
    id_ele_num_list = [id_ele.text for id_ele in id_ele_list]
    if str(required_id) in id_ele_num_list:
        index = id_ele_num_list.index(str(required_id))
    
    else:
        index = search_iteratively(driver,required_id)
    
    reqd_clickable_ele_list = driver.find_elements(By.XPATH,"//span[@data-id='heroField']")
    reqd_clickable_ele = reqd_clickable_ele_list[index]
    reqd_clickable_ele.click()
    time.sleep(2)
    
    attachment_ele_list = driver.find_elements(By.XPATH,"//a[@data-automationid='FieldRenderer-url']")
    attachment_url_list = [attachment_ele.get_attribute('href') for attachment_ele in attachment_ele_list]
    
    attachment_index = 0
    
    for attachment_url in attachment_url_list:
        attachment_index+=1
        attachment_url_new = attachment_url.strip('?web=1')
        
        file_extension = os.path.splitext(attachment_url_new)[-1]
        
        folder_path = '{}/MS-List ID {}'.format(output_attachments_folderpath,required_id)
        
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        
        attachment_path = "{}/attachment-{}{}".format(folder_path,attachment_index,file_extension)
        
        cookies = driver.get_cookies()
        session = requests.Session()
        
        # Add cookies from Selenium to requests session
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # Now download using authenticated session
        response = session.get(attachment_url_new)
        response.raise_for_status()
        
        with open(attachment_path, 'wb') as f:
            f.write(response.content)

    close_btn_ele = driver.find_element(By.XPATH,"//button[contains(@class, 'ms-Button') and contains(@class, 'ms-Button--commandBar') and contains(@class, 'ms-CommandBarItem-link') and contains(@class, 'sp-itemDialog-closeBtn')]")
    close_btn_ele.click()

    go_back_to_home_btn_ele = driver.find_element(By.XPATH,"//button[contains(@class, 'SearchBoxExitButton')]")
    go_back_to_home_btn_ele.click()

    if attachment_index==0:
        print('No Attachments found for id count = {}/{}... - MS List ID: {}'.format(id_count,len(required_id_list_2),required_id))
        
    else:
        print('Attachments extracted for id count = {}/{}... - MS List ID: {}'.format(id_count,len(required_id_list_2),required_id))
        
    print('##################################')

    id_count+=1
    
print('All attachments downloading - Successfully completed')
driver.quit()
print('Browser is successfully quitted...')
