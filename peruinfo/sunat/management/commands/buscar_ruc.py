from django.core.management.base import BaseCommand, CommandError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
options = webdriver.ChromeOptions()
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
import re
import pandas as pd 
from time import sleep
import logging
from peruinfo.sunat.models import Padron
logging.basicConfig(level=logging.WARNING)

class Command(BaseCommand):
    
    help = 'Buscar datos en sunat por ruc'
    success = 0
    error = 0
    
    
    def add_arguments(self, parser):
        pass
        
    def handle(self, *args, **options):
        driver = self.get_driver()
        padron = self.get_data()
        for p in padron:
            self.buscar_ruc(driver, p.ruc)
            self.go_back(driver)
            
        sleep(6)
        # driver.close()
        self.stdout.write(self.style.SUCCESS(f'Pag: {self.success} cargadas correctamente') + self.style.WARNING(f' Pag: {self.error} que no se pudieron cargar'))
        
    def get_data(self, size=100):
        padron = Padron.objects.all()[:size]
        return padron
            
    def get_driver(self):
        url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
        options = webdriver.ChromeOptions()
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        return driver
    
    def go_back(self, driver):
        driver.execute_script("window.history.go(-1)")
        sleep(2)
    
    def buscar_ruc(self, driver, ruc):
        elem = driver.find_element(By.ID, 'txtRuc')
        elem.clear()
        elem.send_keys(ruc)
        driver.find_element(By.ID, 'btnAceptar').click()
        wiat = WebDriverWait(driver, 10)
        elem = wiat.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btnNuevaConsulta, .form-button')))
        
        if elem.get_attribute('value') == 'Anterior':
            elem.click()
            sleep(1)
            self.stdout.write('⚠️  pagina no cargada ' + ruc)
            self.error += 1
            return self.buscar_ruc(driver, ruc)
        self.stdout.write('✅ ruc encontrado ' + ruc)
        self.success += 1
        return elem
    
    def get_ultima_actualizacion(self, driver):
        elem = driver.find_element(By.ID, 'txtRuc')
        elem.clear()
        elem.send_keys('20330407507')
        driver.find_element(By.ID, 'btnAceptar').click()