from django.db import models


class Ubigeo(models.Model):
    codigo_inei = models.CharField(max_length=6, unique=True)
    codigo_reniec = models.CharField(max_length=6, unique=True)
    nombre = models.CharField(max_length=100)
    iso_3166_2 = models.CharField(max_length=6, unique=True)
    fips = models.CharField(max_length=2, unique=True)
    capital = models.ForeignKey('self', null=True, blank=True)
    superficie = models.FloatField(null=True, blank=True)
    altitud = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'ubigeo'
        verbose_name_plural = 'Ubigeo'

    def __str__(self) -> str:
        return f'{self.codigo_inei} - {self.nombre}'
