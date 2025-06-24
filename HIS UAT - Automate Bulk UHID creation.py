#!/usr/bin/env python
# coding: utf-8

# # Requirement: 
# 
# - On HIS UAT, automatically create 10 In-Person (RC) appointment slots of a selected doctor.

# In[3]:


unit='WF'


# In[4]:


bulk_uhid_list_filepath = r"HIS UAT - Bulk UHIDs creation.csv"


# In[5]:


dob_start = '1950-01-01'
test_doctor_name = 'Test Doctor'


# In[6]:


from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import itertools
import time
from datetime import datetime,timedelta
import pandas as pd,numpy as np
from selenium.webdriver.firefox.options import Options
import re,os

from ordered_set import OrderedSet


# In[7]:


def is_valid_time_format(t):
    try:
        datetime.strptime(t.strip().upper(), "%I:%M %p")
        return True
    except ValueError:
        return False


# In[8]:


def user_login(driver):
    userid = driver.find_element("name", "txtUserID")
    
    userid.send_keys("Akhil")
    
    password = driver.find_element("name", "txtPassword")
    
    password.send_keys("Admin@123")
    
    # time.sleep(5)
    
    login_btn = driver.find_element("name", "btnvalid")
    login_btn.click()
    
    time.sleep(2)
    
    if url in driver.current_url.lower():
        login_btn = driver.find_element("name", "btnvalid")
        login_btn.click()


# In[9]:


def click_main_menu(driver):
    main_menu_element = driver.find_element(By.ID, "RAD_SLIDING_PANE_TEXT_ctl00_rsp1")
    main_menu_element.click()


# In[10]:


def click_registration_element(driver):
    registration_element = driver.find_element(
        By.XPATH,
        "//a[@href='#'][span/b[normalize-space(text())='Registration']]"
    )
    
    registration_element.click()


# In[48]:


np.NZERO


# In[58]:


def automate_registration_creation(driver,patient_index,dob_start,df):
    first_name = 'Bulk Testing Case Patient Name'
    middle_name = ''
    last_name = str(patient_index)
    firstdigit_mobile_num = 9
    first_mobile_num = str(firstdigit_mobile_num).zfill(10)[::-1]

    full_name = '{} {} {}'.format(first_name,middle_name,last_name)
    
    if patient_index%2==0:
        title = 'Mrs.'
        gender = 'Female'

    else:
        title = 'Mr.'
        gender = 'Male'

    new_reg_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnNew')
    new_reg_element.click()
    time.sleep(3)

    first_name_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_dropTitle_Arrow')
    first_name_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtFname")
    first_name_element.clear()
    first_name_element.send_keys(first_name)

    last_name_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtLame")
    last_name_element.clear()
    last_name_element.send_keys(last_name)

    gender_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_dropSex_Arrow")
    gender_element.click()
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    my_gender_item = [item for item in items if item.text==gender][0]
    my_gender_item.click()

    dob_start_object = datetime.strptime(dob_start, "%Y-%m-%d").date()
    patient_dob_object = dob_start_object + timedelta(patient_index)
    patient_dob = patient_dob_object.strftime('%Y-%d-%m')
    # print(patient_dob)

    dob_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_dtpDateOfBirth_dateInput')
    # dob_element.clear()
    dob_element.send_keys(patient_dob)
    # time.sleep(3)
    # mother_name = 'Dummy'
    # mother_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_txtMothername')
    # mother_element.clear()
    # mother_element.send_keys(mother_name)
    # mother_element.clear()

    body = driver.find_element(By.TAG_NAME, "body")
    
    body.click()

    time.sleep(2)
    
    patient_address = '{} Residential address'.format(full_name)
    address_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_txtLAddress1')
    address_element.clear()
    address_element.send_keys(patient_address)

    mobile_number = str(int(first_mobile_num)+patient_index)
    mobile_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_txtPMobile')
    mobile_element.clear()
    mobile_element.send_keys(mobile_number)

    email = full_name.lower().replace(' ','_') + '@gmail.com'
    email_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_txtPEmailID')
    email_element.clear()
    email_element.send_keys(email)

    lead_source = 'Walk-in'
    lead_source_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddlLeadSource_Arrow')
    lead_source_element.click()
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    my_lead_source_item = [item for item in items if item.text==lead_source][0]
    my_lead_source_item.click()
    
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    
    provider_doctor_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddlRenderingProvider_Arrow')
    driver.execute_script("arguments[0].click();", provider_doctor_element)
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    # print([item.text for item in items])
    my_provider_doctor_item = [item for item in items if test_doctor_name in item.text][0]
    my_provider_doctor_item.click()

    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    
    identity_number = 'ID-{}'.format(str(patient_index).zfill(5))
    identity_element = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_txtIdentityNumber')
    identity_element.clear()
    identity_element.send_keys(identity_number)

    title_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_dropTitle_Arrow')
    title_element.click()
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    my_title_item = [item for item in items if item.text==title][0]
    my_title_item.click()
    
    save_reg_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnSave')
    save_reg_element.click()

    time.sleep(2)
    proceed_button_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnAntibioticsProceed')
    proceed_button_element.click()

    time.sleep(2)
    uhid_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtAccountNo')
    uhid = uhid_element.get_attribute('value')

    print('UHID: ',uhid)
    temp_df = pd.DataFrame(data=[[uhid,first_name,middle_name,last_name,full_name,mobile_number,email]],columns=df.columns)

    df = pd.concat([df,temp_df])

    return df


# In[12]:


firefox_options = Options()
firefox_options.binary_location = r"C:\Users\nitin.selvam\AppData\Local\Mozilla Firefox\firefox.exe"

service = Service("geckodriver-v0.36.0-win32/geckodriver.exe")
driver = webdriver.Firefox(service=service, options=firefox_options)

#URL of the website
ip_port_details_df = pd.read_excel(r'UAT HIS IP Port details.xlsx')

base_url = ip_port_details_df[ip_port_details_df['Unit']==unit]['IP with Port - UAT HIS application'].values[0]

url = '{}/login'.format(base_url)
 
#opening link in the browser
driver.get(url)


# In[13]:


user_login(driver)


# In[14]:


already_logged_in_ok_button = driver.find_elements("name", "ButtonOk")

if already_logged_in_ok_button!=[] and already_logged_in_ok_button[0].get_property('value') == 'Logout':
    already_logged_in_ok_button[0].click()


# In[35]:


click_main_menu(driver)
click_registration_element(driver)


# In[50]:


counter=10 # Count of how many UHIDs to be created in bulk


# In[60]:


index = -1

if not os.path.exists(bulk_uhid_list_filepath):
    col_list = ["UHID", "First Name", "Middle Name", "Last Name", "Full Name", "Mobile Number", "Email"]
    df = pd.DataFrame(columns=col_list)
    df.to_csv(bulk_uhid_list_filepath,index=False)
    index=0
else:
    df = pd.read_csv(bulk_uhid_list_filepath)
    if len(df)==0:
        index=0

if index == -1:
    fullname_list = list(df.sort_values(by='Full Name')['Full Name'].values)
    numbers = [int(re.findall(r'\d+', fullname)[0]) for fullname in fullname_list]
    numbers.sort()
    index = numbers[-1]

print(index)

for i in range(1,counter+1):
    patient_index = index+i
    print('patient_index',patient_index)
    time.sleep(1)
    df = automate_registration_creation(driver,patient_index,dob_start,df)

df.to_csv(bulk_uhid_list_filepath,index=False)


# In[57]:


df.reset_index(drop=True,inplace=True)

df


# In[ ]:


df.to_csv(bulk_uhid_list_filepath,index=False)


# In[ ]:


save_reg_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnSave')
save_reg_element.click()


# In[ ]:


proceed_button_element = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnAntibioticsProceed')
proceed_button_element.click()


# In[ ]:




