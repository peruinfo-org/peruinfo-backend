from django.db import models


class Padron(models.Model):
    """
    Modelo que representa el padron de contribuyentes de SUNAT
    """
    ruc = models.CharField(max_length=11, unique=True, primary_key=True)
    
    razon_social = models.CharField(max_length=300, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    condicion = models.CharField(max_length=255, null=True, blank=True)
    tipo_contribuyente = models.CharField(max_length=255, null=True, blank=True)
    
    ubigeo = models.CharField(max_length=8, null=True, blank=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    distrito = models.CharField(max_length=150, null=True, blank=True)
    domicilio_fiscal = models.CharField(max_length=350, null=True, blank=True)

    ciiu_v3_principal = models.CharField(max_length=255, null=True, blank=True)
    ciiu_v3_secundario = models.CharField(max_length=255, null=True, blank=True)
    ciiu_v4_principal = models.CharField(max_length=255, null=True, blank=True)

    numero_empleados = models.IntegerField(null=True, blank=True)
    tipo_facturacion = models.CharField(max_length=20, null=True, blank=True)
    tipo_contabilidad = models.CharField(max_length=20, null=True, blank=True)
    comercio_exterior = models.CharField(max_length=20, null=True, blank=True)

    ultima_actualizacion = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Padron'
        verbose_name_plural = 'Padrones'
        indexes = [
            models.Index(fields=['razon_social', 'ruc']),
        ]

    
    def __str__(self) -> str:
        return f'{self.ruc} - {self.razon_social}'
    
    