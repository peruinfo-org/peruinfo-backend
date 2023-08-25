from django.core.management.base import BaseCommand, CommandError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime
from django.utils.timezone import now
import re
import pandas as pd 
from time import sleep
import logging
from peruinfo.sunat.models import Padron
import rich
logging.basicConfig(level=logging.WARNING)

class Command(BaseCommand):
    
    help = 'Buscar datos en sunat por ruc'
    success = 0
    error = 0
    url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
    
    def add_arguments(self, parser):
        parser.add_argument('--ruc', type=str, help='Ruc a buscar')
        parser.add_argument('--size', type=int, help='Cantidad de ruc a buscar', default=10)
        
    def handle(self, *args, **options):

        if options['ruc']:
            ruc = options['ruc']
            driver = self.get_driver()
            if self.buscar_ruc(driver, ruc):
                self.get_data(driver, ruc,  verbose=True)
        else:

            driver = self.get_driver()
            padron = self.get_padron(size=options['size'])
            self.stdout.write(f'Se procesaran {len(padron)} ruc')
            for p in padron:
                if not self.buscar_ruc(driver, p.ruc):
                    continue
                self.get_data(driver, p.ruc, verbose=True)
                self.go_back(driver)

        driver.close()
        self.stdout.write(self.style.SUCCESS(f'Pag: {self.success} cargadas correctamente') + self.style.WARNING(f' Pag: {self.error} que no se pudieron cargar'))
        
    def get_padron(self, size):
        padron = Padron.objects.filter(ultima_consulta_ruc__isnull=True).order_by('ruc')[:size]

        if len(padron) == 0:
            self.stdout.write('No hay ruc para buscar')
            # se buscaran los mas antiguo primero
            padron = Padron.objects.order_by('ultima_consulta_ruc')[:size]
        return padron
            
    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        return driver
    
    def go_back(self, driver):
        driver.execute_script("window.history.go(-1)")
        sleep(2)
    
    def buscar_ruc(self, driver, ruc):
        if driver.current_url != self.url:
            driver.get(self.url)
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
            return 
        self.stdout.write('✅ ruc encontrado ' + ruc)
        self.success += 1
        return elem
    
    def get_data(self, driver, ruc, verbose=False):
        padron = Padron.objects.get(ruc=ruc)
        padron.ultima_consulta_ruc = self._get_ultima_actualizacion(driver, verbose)
        padron.actividad_economica = self._get_actividad_economica(driver, verbose)
        padron.comprobantes = self._get_comprobantes(driver, verbose)
        padron.save()
        self.stdout.write('💾 datos guardados ' + ruc)
    
    def _get_ultima_actualizacion(self, driver, verbose=False):
        try:
            fecha_actualizacion = driver.find_element(By.CSS_SELECTOR, '.panel-footer.text-center').text
            reg_fecha = re.compile(r'(\d{2}/\d{2}/\d{4})')
            fecha_actualizacion = reg_fecha.search(fecha_actualizacion).group(1)
            fecha_actualizacion = datetime.strptime(fecha_actualizacion, '%d/%m/%Y').date()
            if verbose:
                self.stdout.write(f'Ultima actualizacion: {fecha_actualizacion}')
            return fecha_actualizacion
        except Exception as e:
            self.stdout.write(f'Error al obtener la fecha de actualizacion: {e}')
            return now()
    
    def _get_actividad_economica(self, driver, verbose=False):
        try:
            actividad_economica = driver.find_element(By.XPATH, '//*[contains(text(), "Actividad(es) Económica(s)")]')
            actividad_economica = actividad_economica.find_element(By.XPATH, '../..')
            actividad_economica = actividad_economica.find_element(By.TAG_NAME, 'table').get_attribute('outerHTML')
            df = pd.read_html(actividad_economica)[0]
            df = df[0].str.split(' - ', expand=True).rename(columns={0:'tipo', 1:'codigo', 2:'descripcion'})
            result = df.set_index('tipo').to_dict(orient='index')
            if verbose:
                self.stdout.write('Actividad economica')
                rich.print(result)
            return result
        except Exception as e:
            self.stdout.write(f'Error al obtener la actividad economica: {e}')
            return None
        
    
    def _get_comprobantes(self, driver, verbose=False):
        try:
            comprobante = driver.find_element(By.XPATH, '//*[contains(text(), "Comprobantes de Pago")]')
            comprobante = comprobante.find_element(By.XPATH, '../..')\
                .find_element(By.TAG_NAME, 'table').get_attribute('outerHTML')
            df = pd.read_html(comprobante)[0]
            result = df[0].tolist()
            if verbose:
                self.stdout.write('Comprobantes de pago')
                rich.print(result)
            return result
        except Exception as e:
            self.stdout.write(f'Error al obtener los comprobantes: {e}')
            return None
    


