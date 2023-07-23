from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from tqdm import tqdm

from ...models import Padron


class Command(BaseCommand):
    
    help = 'Carga el padron de contribuyentes de SUNAT'
    
    
    def add_arguments(self, parser):
        
        parser.add_argument(
            "--size",
            type=int,
            help="Cantidad de registros a cargar",
        )
        
        parser.add_argument(
            "--padron-sunat",
            action="store_true",
            help="""
                Cargar el padron de contribuyentes de SUNAT
                desde http://www2.sunat.gob.pe/padron_reducido_ruc.zip
            """
        )
    
    def handle(self, *args, **options):
        
        if options['padron_sunat']:
            self.load_padron_sunat(size=options['size'])
            self.stdout.write(self.style.SUCCESS('Padron de contribuyentes de SUNAT cargado exitosamente'))
                
            
    def load_padron_sunat(self, size: int = None):
        """
        Carga el padron de contribuyentes de SUNAT

        Args:
            create (bool, optional): _description_. Defaults to False.
            size (int, optional): _description_. Defaults to None.
        """
    
        url = 'http://www2.sunat.gob.pe/padron_reducido_ruc.zip'
        self.stdout.write(f'Descargando {url}')
        
        df = pd.read_csv(url, encoding='latin-1', sep='|', on_bad_lines='warn')
        if size:
            df = df.iloc[:size]
        
        df['RUC'] = df['RUC'].astype(str).str.zfill(11)
        df.set_index('RUC', inplace=True)
        ruc_list = df.index.tolist()
        
        existing_ruc_list, non_existing_ruc_list = self._exists_ruc(ruc_list)
        
        create_list = []
        for ruc in non_existing_ruc_list:
            row = df.loc[ruc]
            padron = Padron(
                ruc=ruc,
                razon_social=row['NOMBRE O RAZÓN SOCIAL'],
                estado=row['ESTADO DEL CONTRIBUYENTE'],
                condicion=row['CONDICIÓN DE DOMICILIO']
            )
            create_list.append(padron)
            
            
        if create_list:
            self.stdout.write(f'Creando {len(create_list)} registros')
            Padron.objects.bulk_create(create_list)
            
        update_list = []
        for ruc in existing_ruc_list:
            row = df.loc[ruc]
            padron = Padron(
                ruc=ruc,
                razon_social=row['NOMBRE O RAZÓN SOCIAL'],
                estado=row['ESTADO DEL CONTRIBUYENTE'],
                condicion=row['CONDICIÓN DE DOMICILIO']
            )
            update_list.append(padron)
            
        if update_list:
            self.stdout.write(f'Actualizando {len(update_list)} registros')
            Padron.objects.bulk_update(
                update_list,
                ['razon_social', 'estado', 'condicion']
            )

            
    def _exists_ruc(self, ruc_list: list[str]):
        """
        Valida la estructura del RUC

        Args:
            ruc_list (list[str]): Lista de RUC

        return:
            Tuple[list[str], list[str]]: Tupla con dos listas, 
            la primera con los RUC existentes y la segunda con los RUC no existentes
        """
        
        existing_ruc_list = list(Padron.objects.filter(ruc__in=ruc_list).values_list('ruc', flat=True))
        
        non_existing_ruc_list = list(set(ruc_list) - set(existing_ruc_list))
        
        return existing_ruc_list, non_existing_ruc_list
            
                
        