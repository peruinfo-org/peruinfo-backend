from django.db import models


class Padron(models.Model):
    """
    Modelo que representa el padron de contribuyentes de SUNAT
    """
    ruc = models.CharField(max_length=11, unique=True, primary_key=True)
    
    razon_social = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    condicion = models.CharField(max_length=255, null=True, blank=True)
    
    ubigeo = models.CharField(max_length=255, null=True, blank=True)
    departamento = models.CharField(max_length=255, null=True, blank=True)
    provincia = models.CharField(max_length=255, null=True, blank=True)
    distrito = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Padron'
        verbose_name_plural = 'Padrones'
    
    def __str__(self) -> str:
        return f'{self.ruc} - {self.razon_social}'
    

class Establecimiento(models.Model):
    """
    Modelo que representa los establecimientos de un contribuyente
    """
    ruc = models.ForeignKey(Padron, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255, null=True, blank=True)
    tipo = models.CharField(max_length=255, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    actividad_economica = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Establecimiento'
        verbose_name_plural = 'Establecimientos'
        
    def __str__(self) -> str:
        return f'{self.ruc} - {self.codigo} - {self.tipo}'


class 