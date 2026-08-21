from django.db import models


class Genero(models.Model):
    nombre = models.CharField("Nombre", max_length=100)

    class Meta:
        verbose_name = "Genero"
        verbose_name_plural = "Generos"

    def __str__(self):
        return self.nombre


class Director(models.Model):
    nombre = models.CharField("Director", max_length=100)

    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"

    def __str__(self):
        return self.nombre


class Peliculas(models.Model):
  titulo = models.CharField("Titulo", max_length=100)
  duracion = models.DurationField("Duracion") 
  director = models.ForeignKey(Director, on_delete=models.CASCADE, related_name="peliculas")
  genero = models.ForeignKey(Genero, on_delete=models.CASCADE, related_name="peliculas")
  sinopsis = models.CharField("Sinopsis", max_length=300)
  anio = models.IntegerField("Año", null=True, blank=True)
  imagen = models.ImageField("Póster", upload_to="peliculas/posters/", null=True, blank=True)
  
  class Meta:
      verbose_name='Pelicula'
      verbose_name_plural='Peliculas'
  def __str__(self):
      return self.titulo


class DetallePelicula(models.Model):
    TP = "TP"
    M7 = "7"
    M12 = "12"
    M16 = "16"
    M18 = "18"

    CLASIFICACION_EDAD_CHOICES = [
        (TP, "Todas las edades"),
        (M7, "Mayores de 7 años"),
        (M12, "Mayores de 12 años"),
        (M16, "Mayores de 16 años"),
        (M18, "Mayores de 18 años"),
    ]

    pelicula = models.OneToOneField(Peliculas, on_delete=models.CASCADE, related_name="detalles")
    destacada = models.BooleanField("Destacada", default=False)
    fecha_estreno = models.DateField("Fecha de estreno")
    clasificacion = models.CharField( "Clasificación por edad",max_length=3,choices=CLASIFICACION_EDAD_CHOICES,null=True,blank=True, )
    en_cartelera = models.BooleanField("En cartelera", default=False)

    class Meta:
        verbose_name = "Detalle de pelicula"
        verbose_name_plural = "Detalles de peliculas"

    def __str__(self):
        return self.pelicula.titulo


