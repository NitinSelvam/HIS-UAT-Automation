unit='Medcity'


from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
import itertools
import time
import pandas as pd,numpy as np

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

already_logged_in_ok_button = driver.find_elements("name", "ButtonOk")

if already_logged_in_ok_button!=[] and already_logged_in_ok_button[0].get_property('value') == 'Logout':
    already_logged_in_ok_button[0].click()


main_menu_element = driver.find_element(By.ID, "RAD_SLIDING_PANE_TEXT_ctl00_rsp1")
main_menu_element.click()

administration_element = driver.find_element(
    By.XPATH,
    "//a[@href='#'][span/b[normalize-space(text())='Administration']]"
)

administration_element.click()

appt_template_element = driver.find_element(
    By.XPATH,
    "//a[@href='/mpages/providertimings.aspx?Mpg=P120']"
)
appt_template_element.click()

doctor_dropdown_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_TabContainer1_TabVisitMaster_ddlDoctor_Arrow")
doctor_dropdown_element.click()

rc_existing_slots = 'Error'
df = pd.DataFrame()

i=0

while(True):
    doctor_dropdown_element = driver.find_element("id", "ctl00_ContentPlaceHolder1_TabContainer1_TabVisitMaster_ddlDoctor_Arrow")
    doctor_dropdown_element.click()
    html_list = driver.find_element(By.CLASS_NAME, "rcbList")
    items = html_list.find_elements(By.TAG_NAME,"li")
    try:
        doctor_name = items[i].text
    except IndexError as e:
        print("End of the list")
        break
    
    driver.execute_script("arguments[0].click();", items[i])
    time.sleep(3)
    
    record_presence_ele = driver.find_element("id", "ctl00_ContentPlaceHolder1_TabContainer1_TabVisitMaster_gvDoctorTime")

    spans = record_presence_ele.find_elements(By.TAG_NAME, "span")
    th_elements = record_presence_ele.find_elements(By.TAG_NAME, "th")

    if spans and spans[0].text == 'No Record Found.':
        rc_existing_slots = 'No'
    elif th_elements and th_elements[0].text=='Doctor Timings':
        rc_existing_slots = 'Yes'
        
        update_button = driver.find_element("id","ctl00_ContentPlaceHolder1_btnsavedoctortime")
        update_button.click()
    
    print('Doctor name: {} ; RC Existing slots: {}'.format(doctor_name,rc_existing_slots))

    temp_df = pd.DataFrame({'Doctor_Name':[doctor_name],'Regular_Consultation_Existing_Slots':[rc_existing_slots]})

    df = pd.concat([df, temp_df], ignore_index=True)

    time.sleep(3)
    i+=1

html_list = driver.find_element(By.CLASS_NAME, "rcbList")
items = html_list.find_elements(By.TAG_NAME,"li")
doctorname_list = [item.text for item in items]
df_doctorname_list = pd.DataFrame({'doctorname_list':doctorname_list})

final_doctorslots_availability_df = pd.concat([df,df_doctorname_list],axis=1)
final_doctorslots_availability_df['Doctor_Name'] = np.where(final_doctorslots_availability_df['Doctor_Name']=='',final_doctorslots_availability_df['doctorname_list'],final_doctorslots_availability_df['Doctor_Name'])
final_doctorslots_availability_df.drop('doctorname_list',axis=1,inplace=True)
final_doctorslots_availability_df.to_csv('Doctor Slots Availability-{} HIS UAT.csv'.format(unit),index=False)

