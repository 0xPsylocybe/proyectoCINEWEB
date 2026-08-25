"""Trigger que mantiene al día `peliculas_peliculas.recaudacion`.

La recaudación de una película es la suma de lo vendido en taquilla para sus
sesiones. El camino es:

    venta_entrada.sesion_id -> cartelera_sesion.pelicula_id -> peliculas.recaudacion

Se hace con un trigger y no en el código de la vista para que cuadre siempre,
venga la venta del formulario de compra, del Django Admin o de un INSERT a
mano en Supabase.

Los productos del Snack Bar (`venta_producto`) **no** cuentan: la recaudación
es solo taquilla.
"""

from django.db import migrations

CREAR = """
CREATE OR REPLACE FUNCTION cineweb_actualizar_recaudacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Se resta lo que aportaba la fila anterior
    IF (TG_OP = 'DELETE' OR TG_OP = 'UPDATE') THEN
        UPDATE peliculas_peliculas p
           SET recaudacion = p.recaudacion - OLD.total_venta
          FROM cartelera_sesion s
         WHERE s.id = OLD.sesion_id
           AND p.id = s.pelicula_id;
    END IF;

    -- Y se suma lo que aporta la nueva. En un UPDATE puede haber cambiado la
    -- sesión, y con ella la película: por eso se resta de una y se suma a otra.
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE peliculas_peliculas p
           SET recaudacion = p.recaudacion + NEW.total_venta
          FROM cartelera_sesion s
         WHERE s.id = NEW.sesion_id
           AND p.id = s.pelicula_id;
    END IF;

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cineweb_recaudacion ON venta_entrada;

CREATE TRIGGER cineweb_recaudacion
AFTER INSERT OR UPDATE OR DELETE ON venta_entrada
FOR EACH ROW EXECUTE FUNCTION cineweb_actualizar_recaudacion();

-- Cuadre inicial: hasta ahora la recaudación no se actualizaba, así que se
-- recalcula desde las ventas que ya existan.
UPDATE peliculas_peliculas p
   SET recaudacion = COALESCE((
        SELECT SUM(v.total_venta)
          FROM venta_entrada v
          JOIN cartelera_sesion s ON s.id = v.sesion_id
         WHERE s.pelicula_id = p.id
   ), 0);
"""

DESHACER = """
DROP TRIGGER IF EXISTS cineweb_recaudacion ON venta_entrada;
DROP FUNCTION IF EXISTS cineweb_actualizar_recaudacion();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0004_sesion_obligatoria_en_venta"),
        ("cartelera", "0005_sala_columnas_sala_filas"),
        ("peliculas", "0006_carteles_a_la_bbdd"),
    ]

    operations = [
        migrations.RunSQL(CREAR, DESHACER),
    ]
