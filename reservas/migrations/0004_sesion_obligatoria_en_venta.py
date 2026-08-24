"""La sesión pasa a ser obligatoria en VentaEntrada.

Se dejó como opcional al reestructurar el modelo, para poder migrar sobre
las filas que ya existían. Una entrada sin sesión no identifica pelicula,
sala ni horario, y ademas rompe el calculo de recaudacion, que va por
venta_entrada -> sesion -> pelicula.
"""

from django.db import migrations, models
import django.db.models.deletion


def comprobar_sin_huerfanas(apps, schema_editor):
    """Aborta con un mensaje util si quedan ventas sin sesion, en vez de
    dejar que falle la restriccion NOT NULL con un error de la base."""
    VentaEntrada = apps.get_model("reservas", "VentaEntrada")
    huerfanas = VentaEntrada.objects.filter(sesion__isnull=True)
    if huerfanas.exists():
        raise RuntimeError(
            "Hay %d ventas de entradas sin sesion asignada (ids: %s).\n"
            "No se puede hacer el campo obligatorio hasta resolverlas: "
            "asignales una sesion o borralas."
            % (huerfanas.count(),
               ", ".join(str(v.pk) for v in huerfanas[:10]))
        )


class Migration(migrations.Migration):

    dependencies = [
        ("cartelera", "0005_sala_columnas_sala_filas"),
        ("reservas", "0003_entradabutaca_reservabutaca"),
    ]

    operations = [
        migrations.RunPython(comprobar_sin_huerfanas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="ventaentrada",
            name="sesion",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="entradas_vendidas",
                to="cartelera.sesion",
                verbose_name="Sesión",
            ),
        ),
    ]
