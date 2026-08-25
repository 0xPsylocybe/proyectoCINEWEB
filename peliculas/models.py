"""Modelos del catalogo: peliculas, directores, generos, carteles y detalle."""

from django.db import models


class Genero(models.Model):
    """Representa el género cinematográfico de una película (ej. Acción, Drama)."""
    nombre = models.CharField("Nombre", max_length=100)

    class Meta:
        verbose_name = "Genero"
        verbose_name_plural = "Generos"

    def __str__(self):
        return self.nombre


class Director(models.Model):
    """Representa al director o cineasta responsable de una película."""
    nombre = models.CharField("Director", max_length=100)

    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"

    def __str__(self):
        return self.nombre


class Peliculas(models.Model):
  """Modelo principal de películas con información general, duración, director y puntuación."""
  titulo = models.CharField("Titulo", max_length=100)
  duracion = models.DurationField("Duracion")
  director = models.ForeignKey(Director, on_delete=models.CASCADE, related_name="peliculas")
  genero = models.ForeignKey(Genero, on_delete=models.CASCADE, related_name="peliculas")
  sinopsis = models.CharField("Sinopsis", max_length=300)
  anio = models.IntegerField("Año", null=True, blank=True)
  imagen = models.ImageField("Póster", upload_to="peliculas/posters/", null=True, blank=True)
  recaudacion = models.DecimalField("Recaudación", max_digits=10, decimal_places=2, default=0, help_text="Se actualiza automáticamente con las ventas de entradas")
  puntuacion = models.DecimalField("Puntuación", max_digits=3, decimal_places=1, default=0, help_text="Nota media sobre 10. La importa importar_tmdb desde TMDB")

  class Meta:
      verbose_name='Pelicula'
      verbose_name_plural='Peliculas'

  def __str__(self):
      return self.titulo

  def guardar_cartel(self, contenido, nombre=None, tipo="image/jpeg"):
      """Guarda el cartel en la BBDD (y en `imagen`, que sigue marcando que la
      película tiene cartel y da el nombre del fichero).

      `contenido` son los bytes de la imagen.
      """
      from django.core.files.base import ContentFile

      CartelPelicula.objects.update_or_create(
          pelicula=self, defaults={"datos": contenido, "tipo": tipo})

      if nombre:
          # save=False: lo guarda quien llame, junto con el resto de campos
          self.imagen.save(nombre, ContentFile(contenido), save=False)

  @property
  def url_cartel(self):
      """URL desde la que se sirve el cartel, o None si no tiene."""
      from django.urls import reverse

      if not self.imagen:
          return None
      return reverse("cartel_pelicula", args=[self.pk])


class CartelPelicula(models.Model):
    """El cartel guardado en la propia base de datos.

    Va en una tabla aparte, y no como un campo de `Peliculas`, para que las
    consultas del catálogo (`Peliculas.objects.all()`) no arrastren varios MB
    de imágenes. Solo se lee cuando alguien pide la imagen concreta.

    Se hace así porque la base de datos es compartida pero la carpeta `media/`
    no: los ficheros subidos por uno no llegaban al equipo del otro.
    """

    pelicula = models.OneToOneField(
        Peliculas, on_delete=models.CASCADE, related_name="cartel")
    datos = models.BinaryField("Imagen", editable=False)
    tipo = models.CharField("Tipo", max_length=50, default="image/jpeg")
    actualizado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        db_table = "cartel_pelicula"
        verbose_name = "Cartel"
        verbose_name_plural = "Carteles"

    def __str__(self):
        return "Cartel de %s (%d KB)" % (self.pelicula.titulo, len(self.datos) // 1024)


class DetallePelicula(models.Model):
    """Información adicional y estado de exhibición de una película (cartelera, estreno, clasificación)."""
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


