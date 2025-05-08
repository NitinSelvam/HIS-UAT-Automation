#!/usr/bin/env python
# coding: utf-8

# # Requirement: 
# 
# - On HIS UAT, automatically update the appointment slots of all doctors where appointment slots already exist.
# - For doctors whose appointment slots do not exist, leave them as-is without updating.

# In[1]:


unit='WF'


# In[2]:


doctor_name = 'Dr. Somashekar S P'


# In[3]:


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
import re

from ordered_set import OrderedSet


# In[5]:


def is_valid_time_format(t):
    try:
        datetime.strptime(t.strip().upper(), "%I:%M %p")
        return True
    except ValueError:
        return False


# In[6]:


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


# In[7]:


def click_main_menu(driver):
    main_menu_element = driver.find_element(By.ID, "RAD_SLIDING_PANE_TEXT_ctl00_rsp1")
    main_menu_element.click()


# In[8]:


def click_appointment_element(driver):
    appointment_element = driver.find_element(
        By.XPATH,
        "//a[@href='#'][span/b[normalize-space(text())='Appointment']]"
    )
    
    appointment_element.click()


# In[9]:


def click_new_appointment_element(driver):
    appt_new_element = driver.find_element(
        By.XPATH,
        "//a[contains(@href, '/Appointment/AppSchedulerV2.aspx')]"
    )
    
    appt_new_element.click()


# In[10]:


def select_date_pick(driver,date):    
    date_to_pick = date.strftime("%B %e")
    
    date_to_pick = ' '.join([ele for ele in date_to_pick.split(' ') if ele!=''])
    
    date_picker_element = driver.find_element(By.XPATH, "//a[@title='{}']".format(date_to_pick))
    
    driver.execute_script("arguments[0].click();", date_picker_element)


# In[11]:


def show_all_provider_checkbox_select(driver):
    show_all_provider_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_chkShowAllProviders")
    
    is_checked = driver.execute_script("return arguments[0].checked;", show_all_provider_element)
    
    if is_checked==False:
        driver.execute_script("arguments[0].click();", show_all_provider_element)
        time.sleep(1)


# In[23]:


def select_doctor_element_from_all_doctors_list(driver,doctor_name):
    doctor_list_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_RadLstDoctor_Arrow")
    
    doctor_list_element.click()
    
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")

    # print(len([item.text for item in items]))
    doctorname_ele = [item for item in items if item.text == doctor_name][0]
    
    doctorname_ele.click()
    time.sleep(3)


# In[13]:


def get_list_of_all_timeslots(driver):
    slots_scheduler_element = driver.find_element(By.CLASS_NAME, "rsContentTable")
    
    temp_timeslots_list = []
    temp_sub_elements_list = []
    
    # Step 1: Locate the scrollable container
    scroll_container = driver.find_element(By.CLASS_NAME, "rsContentScrollArea")
    
    height = driver.execute_script("return arguments[0].style.height;", scroll_container)
    height_in_px = height.strip('px')
    
    # Step 2: Scroll gradually until the bottom is reached
    last_scroll_top = -1
    while True:
        # Check if we've reached the bottom
        current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroll_container)
        if current_scroll_top == last_scroll_top:
            break
        last_scroll_top = current_scroll_top
    
        timeslots_time_ele = driver.find_element(By.CLASS_NAME, "rsVerticalHeaderTable")
        timeslot_elements = timeslots_time_ele.find_elements(By.TAG_NAME, "tr")
    
        slots_scheduler_element = driver.find_element(By.CLASS_NAME, "rsContentTable")
        sub_elements = slots_scheduler_element.find_elements(By.TAG_NAME, "tr")
        
        inner_list = [ele.text for ele in timeslot_elements if ele.text!='']
        # print(inner_list)
    
        temp_sub_elements_list.append(sub_elements)
        
        temp_timeslots_list.append(inner_list)
    
        # Scroll down a bit
        driver.execute_script("arguments[0].scrollTop += {};".format(height_in_px), scroll_container)
        time.sleep(0.2)  # small wait for content to load/render

    sub_elements_list = [inner for outer in temp_sub_elements_list for inner in outer]
    sub_elements_list = list(OrderedSet(sub_elements_list))
    sub_elements_list = [sub_ele for sub_ele in sub_elements_list if sub_ele.text.strip()=='']
    
    all_timeslots_list = [inner for outer in temp_timeslots_list for inner in outer]
    all_timeslots_list = list(np.unique(all_timeslots_list))
    all_timeslots_list = [t for t in all_timeslots_list if is_valid_time_format(t)]
    all_timeslots_list = sorted(all_timeslots_list, key=lambda x: datetime.strptime(x, '%I:%M %p'))
    
    return sub_elements_list,all_timeslots_list


# In[14]:


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


# In[15]:


user_login(driver)


# In[16]:


already_logged_in_ok_button = driver.find_elements("name", "ButtonOk")

if already_logged_in_ok_button!=[] and already_logged_in_ok_button[0].get_property('value') == 'Logout':
    already_logged_in_ok_button[0].click()


# In[17]:


click_main_menu(driver)


# In[18]:


click_appointment_element(driver)


# In[37]:


click_new_appointment_element(driver)


# In[38]:


date = datetime.now() + timedelta(days=1)  # Select tomorrow's date

select_date_pick(driver,date)


# In[39]:


show_all_provider_checkbox_select(driver)


# In[40]:


select_doctor_element_from_all_doctors_list(driver,doctor_name)


# In[41]:


sub_elements_list,all_timeslots_list = get_list_of_all_timeslots(driver)


# In[42]:


print(len(sub_elements_list))
print(len(all_timeslots_list))


# In[43]:


index=0

while(True):
    if index==10:
        break
    if index>=1:
        driver.switch_to.parent_frame()
        click_new_appointment_element(driver)
        time.sleep(1)
        date = datetime.now() + timedelta(days=1)  # Select tomorrow's date
        select_date_pick(driver,date)
        time.sleep(1)
        show_all_provider_checkbox_select(driver)
        select_doctor_element_from_all_doctors_list(driver,doctor_name)
        sub_elements_list,all_timeslots_list = get_list_of_all_timeslots(driver)

    try:
        sub_elements_list[0].click()

    except IndexError as e:
        print("################################################")
        print("All appointments booked")
        break

    new_appt_select_element = driver.find_element(
        By.XPATH,
        "//a[@href='#'][span[normalize-space(text())='New Appointment']]"
    )
    new_appt_select_element.click()
    time.sleep(3)
    
    driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])
    
    patient_search_btn = driver.find_element(By.ID,'lbtnSearchPatient')
    
    patient_search_btn.click()

    content_row_ele = driver.find_element(By.CLASS_NAME, "rwContentRow")
    driver.switch_to.frame(content_row_ele.find_element(By.NAME, "RadWindowForNew"))

    time.sleep(2)
    # select_patient_link = [ele.find_element(By.TAG_NAME, "a") for ele in patient_table_list_ele][index]

    # select_patient_link.click()
    # driver.switch_to.parent_frame()
    
    # mobile_no_ele = driver.find_element(By.ID,'txtMobile')
    # alternative_mobile_no_ele = driver.find_element(By.ID,'txtAlterNetMobileNo')
    # mobile_no = mobile_no_ele.get_attribute('value')
    # driver.execute_script("arguments[0].setAttribute('value',arguments[1])",alternative_mobile_no_ele, mobile_no)

    # referred_type_list_ele = driver.find_element(By.ID,'dropReferredType_Input')
    # referred_type_list_ele.click()

    # dropdown_ele = driver.find_element(By.ID, "dropReferredType_DropDown")
    # html_list = dropdown_ele.find_element(By.CLASS_NAME, "rcbList")
    # items = html_list.find_elements(By.TAG_NAME,"li")
    
    # self_referred_type_ele = [item for item in items if item.text == 'Self'][0]
    # self_referred_type_ele.click()
    
    # time.sleep(2)

    # make_appointment_button = driver.find_element(By.ID, "btnsave")
    # make_appointment_button.click()

    # break

    patient_table_list_ele = driver.find_elements(
    By.XPATH,
    "//tr[contains(@id, 'gvEncounter_ctl00__')]"
    )
    
    select_patient_link = [ele.find_element(By.TAG_NAME, "a") for ele in patient_table_list_ele][index]
    
    select_patient_link.click()
    driver.switch_to.parent_frame()
    time.sleep(3)
    mobile_no_ele = driver.find_element(By.ID,'txtMobile')
    alternative_mobile_no_ele = driver.find_element(By.ID,'txtAlterNetMobileNo')
    mobile_no = mobile_no_ele.get_attribute('value')
    driver.execute_script("arguments[0].setAttribute('value',arguments[1])",alternative_mobile_no_ele, mobile_no)
    
    referred_type_list_ele = driver.find_element(By.ID,'dropReferredType_Input')
    referred_type_list_ele.click()
    time.sleep(1)
    
    dropdown_ele = driver.find_element(By.ID, "dropReferredType_DropDown")
    html_list = dropdown_ele.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    
    self_referred_type_ele = [item for item in items if item.text == 'Self'][0]
    self_referred_type_ele.click()
    
    time.sleep(2)
    
    make_appointment_button = driver.find_element(By.ID, "btnsave")
    make_appointment_button.click()
    time.sleep(2)
    index+=1
    # break

