#!/usr/bin/env python
# coding: utf-8

# # Requirement: 
# 
# - On HIS UAT, automatically update the appointment slots of all doctors where appointment slots already exist.
# - For doctors whose appointment slots do not exist, leave them as-is without updating.

# In[6]:


unit='WF'


# In[7]:


doctor_name = 'Dr. Somashekar S P'


# In[8]:


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


# In[9]:


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


# In[10]:


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


# In[11]:


already_logged_in_ok_button = driver.find_elements("name", "ButtonOk")

if already_logged_in_ok_button!=[] and already_logged_in_ok_button[0].get_property('value') == 'Logout':
    already_logged_in_ok_button[0].click()


# In[12]:


main_menu_element = driver.find_element(By.ID, "RAD_SLIDING_PANE_TEXT_ctl00_rsp1")

main_menu_element.click()


# In[13]:


appointment_element = driver.find_element(
    By.XPATH,
    "//a[@href='#'][span/b[normalize-space(text())='Appointment']]"
)

appointment_element.click()


# In[25]:


appt_new_element = driver.find_element(
    By.XPATH,
    "//a[contains(@href, '/Appointment/AppSchedulerV2.aspx')]"
)

appt_new_element.click()


# In[26]:


date = datetime.now() + timedelta(days=1)

date_to_pick = date.strftime("%B %e")

date_to_pick = ' '.join([ele for ele in date_to_pick.split(' ') if ele!=''])

date_to_pick

# month = date.strftime("%B")
# year = date.strftime("%Y")
# date_day = date.strftime("%d")

# print(date_to_pick,'--',month,'--',year,'--',date_day)


# In[27]:


date_picker_element = driver.find_element(By.XPATH, "//a[@title='{}']".format(date_to_pick))

driver.execute_script("arguments[0].click();", date_picker_element)


# In[28]:


show_all_provider_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_chkShowAllProviders")

# show_all_provider_element.click()

driver.execute_script("arguments[0].click();", show_all_provider_element)
time.sleep(1)


# In[29]:


doctor_list_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_RadLstDoctor_Arrow")

doctor_list_element.click()

html_list = driver.find_element(By.CLASS_NAME, "rcbList")
items = html_list.find_elements(By.TAG_NAME,"li")

doctorname_ele = [item for item in items if item.text == doctor_name][0]

doctorname_ele.click()
time.sleep(2)


# In[30]:


slots_scheduler_element = driver.find_element(By.CLASS_NAME, "rsContentTable")


# In[31]:


slot_element_list = slots_scheduler_element.find_elements(By.TAG_NAME, "tr")

len(slot_element_list)


# In[32]:


timeslots_time_ele = driver.find_element(By.CLASS_NAME, "rsVerticalHeaderTable")
elements = timeslots_time_ele.find_elements(By.TAG_NAME, "tr")

len(elements)


# In[33]:


timeslot_time_list = [ele.text for ele in elements if ele.text!='']
timeslot_time_list


# In[34]:


from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Locate the scrollable element (change locator accordingly)
scrollable = slots_scheduler_element

# Set scroll parameters
scroll_pause_time = 0.3  # seconds
scroll_step = 100        # pixels per step

# Get initial scroll position and height
last_scroll_position = 0
max_scroll_reached = False

while not max_scroll_reached:
    # Scroll down by scroll_step
    driver.execute_script("arguments[0].scrollTop += arguments[1];", scrollable, scroll_step)
    time.sleep(scroll_pause_time)

    # Get new scroll position
    current_position = driver.execute_script("return arguments[0].scrollTop;", scrollable)
    total_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable)
    client_height = driver.execute_script("return arguments[0].clientHeight;", scrollable)

    # Debug output (optional)
    print(f"Scroll position: {current_position}/{total_height}")

    # If we've reached the bottom, stop
    if current_position + client_height >= total_height:
        max_scroll_reached = True
    elif current_position == last_scroll_position:
        # Nothing is loading anymore, break the loop
        max_scroll_reached = True

    last_scroll_position = current_position

# Once done scrolling, get all sub-elements inside the scrollable area
sub_elements = scrollable.find_elements(By.TAG_NAME, "tr")

print(f"Captured {len(sub_elements)} sub-elements")


# In[35]:


for index in range(len(sub_elements)):
    sub_elements[index].click()

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

    break


# In[36]:


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



# In[38]:


# appt_created_times = []

# appt_created_times.append(timeslot_time_list[index])


# In[40]:


appt_created_times


# In[ ]:


driver.switch_to.default_content()


# In[ ]:


sub_elements[index].click()


# In[ ]:




