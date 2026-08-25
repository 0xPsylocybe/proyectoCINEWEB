# 📋 Seguimiento del proyecto CINEWEB

Documento vivo para registrar **qué hace cada uno**, ir **validando** el trabajo y
tener claros los **siguientes puntos a trabajar**. Actualizadlo conforme avancéis.

## Leyenda de estados

| Símbolo | Estado |
|---------|--------|
| ⬜ | Pendiente |
| 🟡 | En progreso |
| 🔵 | Hecho, pendiente de validar por el compañero |
| ✅ | Validado |
| ⛔ | Bloqueado |

---

## Progreso — Luizay

| Fecha | Tarea | Estado | Notas / validación |
|-------|-------|--------|--------------------|
| 2026-08-21 | App **core**: plantilla base, navbar, sidebar, footer | 🔵 | Bootstrap 5, responsive, preloader con el logo |
| 2026-08-21 | App **core**: inicio, sobre el cine, próximos estrenos | 🔵 | Ver observaciones abajo |
| 2026-08-21 | App **peliculas**: modelos (`Peliculas`, `Director`, `Genero`, `DetallePelicula`) | 🔵 | |
| 2026-08-21 | App **peliculas**: CRUD completo (crear / listar / editar / eliminar) | 🔵 | Con mensajes de Django y subida de póster |
| 2026-08-21 | App **peliculas**: alta rápida de **Género** y **Director** desde el propio listado | 🔵 | Dos formularios en la misma pantalla |
| 2026-08-21 | App **peliculas**: búsqueda por título y filtrado por género | ⬜ | No encontrado en el código |
| 2026-08-21 | **cartelera** (visualización): listado y detalle de película | 🔵 | David lo ha dividido en dos secciones |
| 2026-08-24 | App **usuarios**: login / logout con las vistas genéricas de Django | 🔵 | Sin registro público: los gestores se crean desde el admin |
| 2026-08-24 | App **usuarios**: recuperación de contraseña (4 pantallas) | 🔵 | `password_reset` completo con plantillas propias |
| 2026-08-24 | App **usuarios**: decorador `gestor_required` | 🔵 | Gestor = superusuario o miembro del grupo *Gestores* |

### Observaciones sobre el código de Luizay (revisión de David, 2026-08-25)

Todas sus pantallas responden correctamente; no hay ninguna que reviente. Lo que
convendría repasar:

1. ⬜ **`detalle_pelicula` es inalcanzable**: la vista existe en
   `peliculas/views.py` pero no tiene ruta en `peliculas/urls.py`, y su
   plantilla `templates/peliculas/detalle_pelicula.html` no existe. Tal y como
   está, si se enruta dará error de plantilla. Decidir: completarla o borrarla.
2. ⬜ **Errata en una URL**: `pelicula/<pk>/editar_pelicual` (el `name` sí está
   bien escrito, solo se ve en la barra del navegador).
3. ⬜ **`templates/restauracion/snack_bar.html` está vacío** y nadie lo usa. El
   Snack Bar se sirve desde `templates/restauracion/catalogo.html` (David).
   Decidir con cuál os quedáis para no tener dos.
4. ⬜ **La portada muestra las 35 películas**, también las que no están en
   cartelera. `core/views.py` usa `Peliculas.objects.all()`. La cartelera ya
   filtra por `en_cartelera`; la portada quizá debería hacer lo mismo.
5. ✅ **`/proximos_estrenos/` salía vacía**: filtraba por `fecha_estreno` futura
   y, con las fechas reales de TMDB, ninguna lo cumplía. Unificado el
   2026-08-25: ahora usa el mismo criterio y el mismo orden que la cartelera
   (todo lo que no esté en cartelera, por puntuación descendente).
6. ⬜ Los **mensajes de commit** son casi todos "actualizaciones", lo que hace
   difícil seguir qué cambió en cada uno.

## Progreso — David

| Fecha | Tarea | Estado | Notas / validación |
|-------|-------|--------|--------------------|
| 2026-08-21 | App **usuarios**: autenticación (login/logout) | 🔵 | |
| 2026-08-21 | App **usuarios**: roles y permisos + decorador `@gestor_required` | 🔵 | Protegido a nivel de URL, no solo ocultando botones |
| 2026-08-21 | **cartelera** (gestión): modelos `Sala`, `Sesion` + admin | 🔵 | Migrado y en uso |
| 2026-08-23 | **cartelera**: CRUD de sesiones + generación automática | 🔵 | `regenerar_sesiones` y vista "rellenar" |
| 2026-08-23 | **cartelera**: validación de solapamientos entre sesiones | 🔵 | 15 min publicidad + película + 20 min limpieza |
| 2026-08-24 | **cartelera**: `Sala.precio_entrada` — el precio depende de la sala | 🔵 | Editable desde el listado del admin |
| 2026-08-24 | **peliculas**: campo `recaudacion` (solo lectura) | 🔵 | Lo actualizará el trigger |
| 2026-08-24 | **restauracion**: modelo `Categoria` + FK en `Producto` | 🔵 | 5 categorías, 29 productos |
| 2026-08-24 | **restauracion**: catálogo público del Snack Bar | 🔵 | Falta que el botón ➕ añada al carrito |
| 2026-08-24 | App **reservas**: carrito → confirmación → compra | 🔵 | `VentaEntrada` pasa a referenciar la sesión |
| 2026-08-24 | **reservas**: pago con validación de tarjeta (Luhn) | 🔵 | No se persiste ningún dato de tarjeta |
| 2026-08-25 | **reservas**: selección de butacas + reserva de 30 min | 🔵 | `UniqueConstraint` en BBDD contra doble venta |
| 2026-08-25 | **peliculas**: corregir fichas y traer carteles de TMDB | 🔵 | `corregir_peliculas` + `importar_tmdb` |
| 2026-08-25 | **cartelera**: dividir en *Cartelera* y *Próximos estrenos* | 🔵 | |
| 2026-08-25 | **peliculas**: carteles guardados en la BBDD (`CartelPelicula`) | 🔵 | La carpeta `media/` no se comparte y las imágenes salían rotas |
| 2026-08-25 | Lógica de la BBDD: **trigger de recaudación** | 🔵 | `reservas/0005_trigger_recaudacion` |
| 2026-08-25 | **cartelera**: filtros y paginación en `/cartelera/sesiones/` | 🔵 | Por película, sala y rango de fechas |
| 2026-08-25 | **reservas**: resguardo de compra con localizador | 🔵 | Imprimible |
| 2026-08-25 | Documentación: README de puesta en marcha | 🔵 | Sección 7 |
| 2026-08-25 | Configuración por `.env` (BBDD, SECRET_KEY, TMDB) | 🔵 | Con `.env.example` de plantilla |

---

## Próximos puntos a trabajar

Marcad con quién lo coge y su estado.

### 🔧 Configuración base (común)
1. ✅ Registrar las 6 apps en `INSTALLED_APPS` (`config/settings.py`).
2. ✅ Configurar la conexión a **PostgreSQL** (Supabase).
3. ✅ Ajustes de localización (`LANGUAGE_CODE = es-es`, `TIME_ZONE = Europe/Madrid`).
4. ✅ `templates/` y `static/` en raíz, enlazadas en `settings.py`.

### 🗄️ Modelos y base de datos
5. ✅ Modelos de las cinco apps, migrados.
6. ✅ Triggers/SQL a medida en una migración `RunSQL` — hecho el de recaudación.
7. ✅ Modelos registrados en el **Django Admin**.
8. ✅ Superusuario, grupo *Gestores* y datos de prueba.

### 🌐 URLs, vistas y plantillas
9. ✅ URLs modulares por app con `include()`.
10. ✅ Plantilla base con Bootstrap, navbar y sidebar.
11. ✅ Página de **cartelera**, ya dividida en *Cartelera* y *Próximos estrenos*.
12. ✅ Página de **detalle** de película con horarios y filtro por tipo de sala.
13. ⬜ **Búsqueda** por título y **filtrado** por género (Luizay).

### 🔐 Usuarios y permisos
> Decisión: **sysadmin** + **gestores** (con permisos) + **visitantes anónimos**.
> La compra de entradas y productos es anónima (sin login).
14. ✅ Login / logout para gestores y sysadmin.
15. ✅ Grupo de **gestores** con sus permisos.
16. ✅ Vistas de gestión protegidas a nivel de URL con `@gestor_required`.
17. ✅ Compra de entradas y productos **sin iniciar sesión**.

### ✏️ Gestión (CRUD)
18. ✅ CRUD de **películas**.
19. ✅ CRUD de **sesiones**, más generación automática.
20. ✅ Mensajes de Django (creado / editado / eliminado / error).

### 🎟️ Venta (David)
21. ✅ Carrito, confirmación y compra realizada.
22. ✅ Butacas con reserva temporal de 30 minutos.
23. ⬜ Que el botón ➕ del Snack Bar añada el producto al carrito. *(aparcado:
    es un extra, se hará al final)*
24. ✅ Resguardo de compra con localizador, butacas y desglose de lo pagado.
25. ✅ Trigger de recaudación, con el `DELETE` contemplado para las anulaciones.

### 🗂️ Gestión de sesiones (David)
26. ✅ Filtrar por película en `/cartelera/sesiones/` (y también por sala).
27. ✅ Filtrar por rango de fechas, combinable con lo anterior.
28. ✅ Mostrar la fecha de la sesión en la tarjeta, más paginación de 24 en 24.

### ✅ Cierre
29. ✅ Completar el README (instalación, BBDD, migraciones, permisos, ejecución).
29b. ✅ Configuración por `.env`, con `.env.example` como plantilla.
30. ⬜ Pruebas de instalación desde cero siguiendo el README.
31. ⬜ Revisión cruzada del código del compañero.
32. ⬜ Tests unitarios y de integración.

---

## Validaciones / decisiones

Anotad aquí acuerdos o validaciones puntuales (fecha — qué se validó — quién).

| Fecha | Decisión / validación | Quién |
|-------|-----------------------|-------|
| 2026-08-20 | Roles: sysadmin + gestores con permisos + visitantes anónimos. Compra de entradas y comida/bebida **sin login**. | Luizay & David |
| 2026-08-20 | Naming: modelos PascalCase singular + `db_table` snake_case singular. Sesiones = modelo `Sesion` (tabla `sesion`). | Luizay & David |
| 2026-08-20 | Consistencia en la escritura del código (nomenclatura, estilo) y en las tipologías/tipos de datos usados en los modelos. | Luizay & David |
| 2026-08-20 | Columnas con convención Django: **PK `id`**, **FK `<campo>_id`**; nombres de tabla vía `db_table` (snake_case singular). | Luizay & David |
| 2026-08-20 | ✅ **APROBADO el 2026-08-25**: guardar las imágenes en la **BBDD** en vez de solo en el sistema de archivos. Ver detalle abajo. | Luizay & David |
| 2026-08-24 | El **precio de la entrada depende de la sala** (`Sala.precio_entrada`), no de la película. | David |
| 2026-08-24 | La compra **no tiene pasarela de pago real**: se validan los datos de la tarjeta pero no se guardan ni se envían a ningún sitio. | David |
| 2026-08-25 | Una **entrada = una butaca**. Desaparece el campo "cantidad de entradas" del carrito: la cantidad sale del número de butacas elegidas. | David |
| 2026-08-25 | Las butacas se **bloquean 30 minutos** desde que se eligen. El bloqueo caducado se libera solo; no hace falta cron. | David |
| 2026-08-25 | *Próximos estrenos* = todas las películas que **no** estén en cartelera (sin mirar la fecha de estreno). Aplicado ya en las dos pantallas. | David |
| 2026-08-25 | Los **carteles** no se versionan (`media/` está en `.gitignore`): cada uno los genera con `importar_tmdb`. | David |
| 2026-08-25 | *Próximos estrenos* se ordena por **puntuación** descendente. La nota es la de **TMDB**, no la de IMDb (TMDB no la expone; haría falta OMDb con otra clave). Campo `Peliculas.puntuacion`. | David |
| 2026-08-25 | ✅ Botón **"Buscar en TMDB"** al dar de alta o editar una película: rellena la ficha y propone el cartel, y el gestor revisa antes de guardar. Toca la plantilla de Luizay, que debería echarle un ojo. Ver detalle abajo. | David → Luizay |
| 2026-08-25 | El generador de sesiones **ya no crea pases solapados** (había 407 imposibles de proyectar). Como efecto, la programación pasa de ~535 sesiones a 225. | David |
| 2026-08-25 | ✅ Nuevas **horas de pase**: L-V no se abre antes de las 17:00, matinal solo en fin de semana, último pase de viernes y sábado a la 1:00 y sin películas de más de 2h en esa franja. Ver detalle abajo. | David & Luizay |

---

## ✅ Carteles guardados en la base de datos

**Fecha:** 2026-08-25 · Retoma la propuesta que estaba en revisión desde el 20/08.

### El problema que lo provocó

A Luizay le salían las imágenes rotas. La causa: **compartimos base de datos
(Supabase) pero no la carpeta `media/`**, que está en `.gitignore`. La BBDD
guardaba la ruta del cartel y en su equipo ese fichero no existía.

Antes sí las veía, pero por un descuido: hasta el 21/08 no había `MEDIA_ROOT`,
así que Django dejaba los ficheros subidos en la raíz del proyecto
(`peliculas/posters/`), que **sí** está versionada, y viajaban por git sin
querer. Al configurar `MEDIA_ROOT` todo lo nuevo pasó a `media/`, ignorado, y
el problema quedó a la vista.

### Cómo se ha hecho

- Modelo **`CartelPelicula`** (tabla `cartel_pelicula`), con el binario, el tipo
  y la fecha. Va en **tabla aparte** y no como un campo de `Peliculas`: si el
  binario estuviera en `Peliculas`, cada `Peliculas.objects.all()` de la
  cartelera se traería varios MB de imágenes desde Supabase.
- Vista **`/peliculas/cartel/<id>/`** que sirve la imagen, con cabecera de
  caché de un día. Si una película aún no tiene el cartel en la BBDD, cae al
  fichero de `media/` (compatibilidad mientras se migra).
- `Peliculas.guardar_cartel()` deja el cartel en los dos sitios, y
  `Peliculas.url_cartel` da la URL. Lo usan el alta, la edición, el botón de
  TMDB y el comando `importar_tmdb`.
- Migración **`0006_carteles_a_la_bbdd`**: sube a la BBDD los ficheros que ya
  hubiera en disco. Subió los 35 carteles, **3,1 MB**.
- El campo `imagen` se mantiene: sigue indicando si una película tiene cartel y
  guarda el nombre del fichero.

### Qué tiene que hacer Luizay

Solo `git pull` y `python manage.py migrate`. Los carteles ya están en la BBDD
compartida, así que los verá sin descargar nada.

### A tener en cuenta

- La BBDD engorda ~3 MB con 35 carteles (~90 KB cada uno). El plan gratuito de
  Supabase da 500 MB, así que hay margen de sobra, pero conviene no subir
  imágenes enormes desde el formulario.
- Las imágenes las sirve ahora Django, no el servidor de ficheros. Con la caché
  de un día es asumible para este proyecto; en producción real se pondría
  delante un CDN o almacenamiento de objetos.

---

## 🔵 Propuesta pendiente de revisión — botón "Buscar en TMDB"

**Quién la propone:** David · **Quién decide:** Luizay · **Fecha:** 2026-08-25

### Qué es

Al dar de alta una película, escribir el título y pulsar un botón **"Buscar en
TMDB"** que rellene solo el resto del formulario: sinopsis, duración, año,
género, director, puntuación y el cartel. El gestor revisa lo que ha salido y
guarda; si no le convence, lo corrige a mano antes de dar a guardar.

La lógica ya existe: es la misma que usa el comando `importar_tmdb`, que fue
con el que se trajeron los 35 carteles y sus fichas.

### Por qué con un botón y no automático al guardar

Se valoró completar los datos solos con un `post_save`, sin botón. Se descarta
porque **TMDB acierta casi siempre, pero no siempre**: buscando "Dune" puede
devolver la de Villeneuve (2021) o la de Lynch (1984). Con el botón el gestor ve
la ficha antes de aceptarla; en automático entraría en la BBDD sin que nadie la
mire, que es justo como el catálogo acabó teniendo *La zona de interés*
atribuida a Christopher Nolan.

### Qué habría que tocar

1. Sacar la lógica de TMDB del comando a un módulo `peliculas/tmdb.py` (ahora
   vive dentro de la clase `Command` y desde una vista no se puede usar).
2. Un endpoint `/peliculas/buscar-tmdb/?titulo=...` que devuelva JSON,
   protegido con `@gestor_required`.
3. Un poco de JavaScript en el formulario para volcar la respuesta en los campos.
4. Al guardar: crear el director y el género si no existen, y descargar el cartel.

### Cómo quedó resuelto cada punto

- **Toca `templates/peliculas/nueva_pelicula.html`, que es de Luizay.** Se ha
  tocado lo mínimo: un bloque nuevo antes del `<form>`, dos campos ocultos y un
  `<script>` al final. No se ha modificado el renderizado de los campos ni la
  vista previa del póster que ya había. ⚠️ **Luizay: avisa si prefieres otra
  cosa.**
- **Equipos sin `.env`**: `tmdb.hay_clave()` decide si el botón se pinta. Sin
  clave el bloque no aparece y el formulario funciona como siempre; si aun así
  se llama al endpoint, responde 502 con el texto de qué hay que configurar,
  nunca un error 500.
- **`DetallePelicula`**: queda fuera de momento. El formulario de alta no
  incluye ese modelo y añadirlo daba para otra tarea. La fecha de estreno sí la
  rellena `importar_tmdb` en lote.

### Estado

✅ **Hecho** el 2026-08-25. Botón "Buscar en TMDB" en el alta y en la edición de
película. Queda pendiente que Luizay revise el cambio en su plantilla.

---

## 🔵 Propuesta pendiente de revisión — horas de pase de las sesiones

**Quién la propone:** David · **Quién decide:** Luizay & David · **Fecha:** 2026-08-25

### El problema

Las horas de pase están fijas en `HORARIOS_POR_DIA`
(`cartelera/management/commands/regenerar_sesiones.py`) y son cada dos horas:
**18, 20 y 22** entre semana, más 12, 14 y 00 los fines de semana.

Esas horas suponen películas de hora y media. Pero una sesión ocupa la sala
**15 min de publicidad + la película + 20 min de limpieza**, y el catálogo actual
tiene películas largas:

| Película | Dura | Empieza a las 18:00 y la sala queda libre a las |
|----------|------|--------------------------------------------------|
| The Brutalist | 215 min | 22:10 |
| Wicked | 162 min | 21:17 |
| Oppenheimer | 180 min | 21:35 |

Es decir, **el pase de las 20:00 no cabe** en esa sala. Antes el generador los
creaba igual (había **407 sesiones solapadas** en la BBDD, imposibles de
proyectar). Desde el 2026-08-25 el generador respeta la ocupación, así que ya no
se solapan, pero como consecuencia **descarta 153 huecos** y la programación baja
de ~535 sesiones a **225**.

### Opciones

1. **Dejarlo como está.** 225 sesiones en 14 días, 15-16 pases por película. Es
   una programación realista, solo que más corta.
2. **Espaciar las horas** a algo como **16:00, 19:30 y 23:00** entre semana. Con
   3h30 de margen entra casi cualquier película del catálogo y se aprovechan las
   tres franjas.
3. **Horas por duración**: en vez de una lista fija, encadenar los pases desde la
   hora de apertura según lo que dure cada película (lo que hace un cine de
   verdad). Es lo más flexible y lo que más trabajo lleva.

### Cómo quedó

✅ **Resuelto el 2026-08-25** con la opción 2, más las reglas que faltaban:

| Día | Pases |
|-----|-------|
| Lunes a jueves | 17:00 · 19:30 · 22:00 |
| Viernes | 17:00 · 19:30 · 22:00 · 01:00 |
| Sábado | 12:00 · 14:30 · 17:00 · 19:30 · 22:00 · 01:00 |
| Domingo | 12:00 · 14:30 · 17:00 · 19:30 · 22:00 |

- **De lunes a viernes no se abre antes de las 17:00.** Matinal solo el fin de semana.
- **El último pase de viernes y sábado es a la 1:00**, y en esa franja **no se
  programan películas de más de 2 horas**.
- Los saltos son de 2h30: con pases cada dos horas solo caben películas de hasta
  85 minutos, contando publicidad y limpieza.

Resultado: **249 sesiones** (antes 225) y cada película en 4-6 salas en vez de 2-3.

Las reglas viven en `cartelera/programacion.py`, que ahora comparten el comando
`regenerar_sesiones` y la vista "Rellenar automáticamente". Antes cada uno tenía
su propia tabla de horarios y generaban programaciones distintas.

### ⚠️ Dos fallos que aparecieron al hacerlo

1. **Toda la programación estaba corrida dos horas.** Se construían las horas con
   `timezone.now().replace(hour=17)`, que son las 17:00 **UTC**: en Madrid, las
   19:00. Por eso "las 22:00" caían a las 00:00 y las películas largas se colaban
   en la madrugada. Ahora se construyen en hora local con `make_aware`.
2. **`--borrar` reventaba si había entradas vendidas**, porque `VentaEntrada.sesion`
   es `PROTECT`. Ahora esas sesiones se conservan, se avisa de ello y se respeta
   su ocupación al reprogramar. Lo mismo en la vista de rellenar.
