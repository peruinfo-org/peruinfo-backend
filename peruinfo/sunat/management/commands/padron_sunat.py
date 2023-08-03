from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
import tempfile
from tqdm import tqdm
import pandas as pd
import time
from datetime import datetime
import os 
from django.conf import settings


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
            "--batch-size",
            type=int,
            help="Cantidad de registros a cargar por lote",
        )

    
    def handle(self, *args, **options):
        self.load_padron_sunat(size=options['size'], batch_size=options['batch_size'])
        self.stdout.write(self.style.SUCCESS('Padron de contribuyentes de SUNAT cargado exitosamente'))            
            
    def load_padron_sunat(self, size: int, batch_size: int):
        """
        Carga el padron de contribuyentes de SUNAT

        Args:
            size (int, optional): _description_. Defaults to None.
            batch_size (int, optional): _description_. Defaults to 1000.
        """
    
        df_padron_open_data = self._read_padron_sunat_datosabiertos()
        df_padron = self._read_padron_sunat()

        df = pd.concat([df_padron, df_padron_open_data], join='inner', axis=1)
        
        if size:
            df = df.iloc[:size]
            
        # domicilio fiscal
        df['domicilio_fiscal'] = df.apply(self._domicilio_fiscal, axis=1)

        def process_batch(df: pd.DataFrame):
            ruc_list = df.index.tolist()
            
            existing_ruc_list, non_existing_ruc_list = self._exists_ruc(ruc_list)

            # buscar datos de los ruc que no existen en la base de datos
            create_list = []
            for ruc in non_existing_ruc_list:
                row = df.loc[ruc]
                padron = self._padron_object(row)
                create_list.append(padron)
            
            # si encuentra datos, los crea
            if create_list:
                Padron.objects.bulk_create(create_list)
                self.stdout.write(f'    ∟ Creando {len(create_list)} registros')

            # buscar datos de los ruc que existen en la base de datos 
            update_list = []
            for ruc in existing_ruc_list:
                row = df.loc[ruc]
                padron = self._padron_object(row)
                update_list.append(padron)
                
            # si encuentra datos, los actualiza
            if update_list:
                Padron.objects.bulk_update(
                    update_list,
                    [
                        'razon_social', 'estado', 'condicion', 'tipo_contribuyente',
                        'ubigeo', 'departamento', 'provincia', 'distrito', 'domicilio_fiscal',
                        'ciiu_v3_principal', 'ciiu_v3_secundario', 'ciiu_v4_principal',
                        'numero_empleados', 'tipo_facturacion', 'tipo_contabilidad', 'comercio_exterior',
                        'ultima_actualizacion'
                    ]
                )
                self.stdout.write(f'    ∟ Actualizando {len(update_list)} registros')

        self.stdout.write(f'Se procesaran {len(df)} registros')
        # procesar en lotes
        for i in range(0, len(df), batch_size):
            self.stdout.write(f'—  Procesando batch {i} - {i+batch_size}')
            process_batch(df.iloc[i:i+batch_size])
            time.sleep(1)

    def _padron_object(self, row):
        """
        Crea un objeto Padron a partir de una fila del DataFrame
        Args:
            row (pd.Series): Fila del DataFrame
        Returns:
            Padron: Objeto Padron
        """
        padron = Padron(
            ruc=row.name,
            # datos generales
            razon_social=row['NOMBRE O RAZÓN SOCIAL'],
            estado=row['ESTADO DEL CONTRIBUYENTE'],
            condicion=row['CONDICIÓN DE DOMICILIO'],
            tipo_contribuyente=row['Tipo'],
            # direccion
            ubigeo=row['UBIGEO'],
            departamento=row['Departamento'],
            provincia=row['Provincia'],
            distrito=row['Distrito'],
            domicilio_fiscal=row['domicilio_fiscal'],
            # actividad economica
            ciiu_v3_principal=row['Actividad_Economica_CIIU_revision3_Principal'],
            ciiu_v3_secundario=row['Actividad_Economica_CIIU_revision3_Secundaria'],
            ciiu_v4_principal=row['Actividad_Economica_CIIU_revision4_Principal'],
            # datos adicionales
            numero_empleados=row['NroTrab'],
            tipo_facturacion=row['TipoFacturacion'],
            tipo_contabilidad=row['TipoContabilidad'],
            comercio_exterior=row['ComercioExterior'],
            # fecha de actualizacion
            ultima_actualizacion=timezone.now()
        )
        padron.clean()
        return padron
            
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
    
    def _domicilio_fiscal(self, row):
        """
        Obtiene el domicilio fiscal
        df.apply(self._domicilio_fiscal, axis=1)
        """
        text = ''
        if row['TIPO DE VÍA']:
            text += f'{row["TIPO DE VÍA"]} '

        if row['NOMBRE DE VÍA']:
            text += f'{row["NOMBRE DE VÍA"]} '

        if row['CÓDIGO DE ZONA']:
            text += f'{row["CÓDIGO DE ZONA"]} '

        if row['TIPO DE ZONA']:
            text += f'{row["TIPO DE ZONA"]} '

        if row['NÚMERO']:
            text += f'{row["NÚMERO"]} '
        
        if row['INTERIOR']:
            text += f'Int. {row["INTERIOR"]} '
        
        if row['LOTE']:
            text += f'Lote {row["LOTE"]} '

        if row['DEPARTAMENTO']:
            text += f'Dpto. {row["DEPARTAMENTO"]} '

        if row['MANZANA']:
            text += f'Mza. {row["MANZANA"]} '
        
        if row['KILÓMETRO']:
            text += f'Km. {row["KILÓMETRO"]} '

        return text.strip()


    def _read_padron_sunat(self):
        """
        Lee el padron de contribuyentes de SUNAT

        return DataFrame
        """

        url = 'http://www2.sunat.gob.pe/padron_reducido_ruc.zip'
        file_path = self._download(url)
        df = pd.read_csv(
            file_path, 
            encoding='latin-1', sep='|', on_bad_lines='warn', 
            dtype={
                'RUC': str,
                'UBIGEO': str,
                'NOMBRE O RAZÓN SOCIAL': str,
                'ESTADO DEL CONTRIBUYENTE': str,
                'CONDICIÓN DE DOMICILIO': str,
            }, 
            na_values=['-'],
            index_col='RUC')
        return df
    
    def _read_padron_sunat_datosabiertos(self):
        """
        Lee el padron de contribuyentes de SUNAT desde datosaabiertos.gob.pe
        """
        date = datetime.now().strftime('%Y%m%d')
        url = 'https://www.datosabiertos.gob.pe/sites/default/files/PadronRUC_202307.zip'

        file_path = self._download(url)
        df = pd.read_csv(
            file_path,
            encoding='latin-1', 
            dtype={
                'RUC': str,
                'UBIGEO': str,
            },
            na_values=['NO DISPONIBLE'],
            index_col='RUC'
        )
        # drop na
        not_include = [
            'PERSONA NATURAL SIN EMPRESA',
            'PERSONA NATURAL CON EMPRESA UNIPERSONAL',
            'SUCESION INDIVISA SIN EMPRESA',
            'SUCESION INDIVISA COM EMPRESA UNIPERSONAL',
            'SOCIEDAD CONYUGAL SIN EMPRESA',
            'SOCIEDAD CONYUGAL CON EMPRESA UNIPERSONAL'
        ]
        df = df[~df['Tipo'].isin(not_include)]
        df.dropna(inplace=True)
        return df
        
    def _download(self, url: str):
        """
        Descarga un archivo desde una URL
        Args:
            url (str): URL del archivo a descargar
        return:
            str: Ruta del archivo descargado
        """
        self.stdout.write(f'Descargando {url}')

        file_name = url.split('/')[-1]
        file_path = os.path.join(settings.BASE_DIR, '.tmp', file_name)

        # verificar si el archivo ya existe
        if os.path.exists(file_path):
            self.stdout.write(f'El archivo {file_name} ya ha sido descargado')
            return file_path
        
        # Crear el directorio temporal
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:

            # Realizar una solicitud HTTP para obtener el contenido del archivo
            with requests.get(url, stream=True) as response:
                total_size = int(response.headers.get('content-length', 0))

                # Descargar el archivo y mostrar el progreso con un ProgressBar
                with open(file_path, 'wb') as file:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Descargando") as pbar:
                        for chunk in response.iter_content(1024):
                            if not chunk:
                                break
                            file.write(chunk)
                            pbar.update(len(chunk))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al descargar {url}'))
            os.remove(file_path)
            raise e
        
        return file_path
