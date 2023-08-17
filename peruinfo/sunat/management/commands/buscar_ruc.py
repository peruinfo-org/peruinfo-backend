from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
driver.get(url)

elem = driver.find_element(By.ID, 'txtRuc')
elem.clear()
elem.send_keys('20330407507')
driver.find_element(By.ID, 'btnAceptar').click()

# comprobante de pago
elem = driver.find_element(By.ID, 'btnCriterio')


import re
date_str = driver.find_element(By.CSS_SELECTOR, '.panel-footer.text-center').text
date_str = re.findall(r'\d{2}/\d{2}/\d{4}', date_str)[0]
date_str

from datetime import datetime

# conver date string to datetime object
date = datetime.strptime(date_str, '%d/%m/%Y')
print(date)

query_text = 'Actividad(es)'
elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{query_text}')]")


elem.find_element(By.XPATH, '..').get_attribute('outerHTML')