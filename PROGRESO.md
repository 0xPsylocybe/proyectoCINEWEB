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
|       | Lógica de la BBDD (trigger de recaudación) | 🟡 | Lo lleva David |

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
6. 🟡 Triggers/SQL a medida en una migración `RunSQL` — pendiente el de recaudación.
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
23. ⬜ Que el botón ➕ del Snack Bar añada el producto al carrito.
24. ⬜ Mostrar en "compra realizada" qué se ha comprado (con las butacas).
25. ⬜ Trigger de recaudación (contemplando el `DELETE` para las anulaciones).

### 🗂️ Gestión de sesiones (David)
26. ⬜ Filtrar por película en `/cartelera/sesiones/`.
27. ⬜ Filtrar por fecha.
28. ⬜ Mostrar la fecha de la sesión en la tabla.

### ✅ Cierre
29. ⬜ Completar el README (instalación, BBDD, migraciones, permisos, ejecución).
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
| 2026-08-20 | 🔵 **EN REVISIÓN** (pendiente de aprobar Luizay): guardar las imágenes en la **BBDD** usando Pillow, en vez de en el sistema de archivos. A decidir por Luizay. | David → Luizay |
| 2026-08-24 | El **precio de la entrada depende de la sala** (`Sala.precio_entrada`), no de la película. | David |
| 2026-08-24 | La compra **no tiene pasarela de pago real**: se validan los datos de la tarjeta pero no se guardan ni se envían a ningún sitio. | David |
| 2026-08-25 | Una **entrada = una butaca**. Desaparece el campo "cantidad de entradas" del carrito: la cantidad sale del número de butacas elegidas. | David |
| 2026-08-25 | Las butacas se **bloquean 30 minutos** desde que se eligen. El bloqueo caducado se libera solo; no hace falta cron. | David |
| 2026-08-25 | *Próximos estrenos* = todas las películas que **no** estén en cartelera (sin mirar la fecha de estreno). Aplicado ya en las dos pantallas. | David |
| 2026-08-25 | Los **carteles** no se versionan (`media/` está en `.gitignore`): cada uno los genera con `importar_tmdb`. | David |
| 2026-08-25 | *Próximos estrenos* se ordena por **puntuación** descendente. La nota es la de **TMDB**, no la de IMDb (TMDB no la expone; haría falta OMDb con otra clave). Campo `Peliculas.puntuacion`. | David |
| 2026-08-25 | 🔵 **EN REVISIÓN** (pendiente de opinar Luizay): botón **"Buscar en TMDB"** al dar de alta una película. Ver propuesta detallada abajo. | David → Luizay |
| 2026-08-25 | El generador de sesiones **ya no crea pases solapados** (había 407 imposibles de proyectar). Como efecto, la programación pasa de ~535 sesiones a 225. | David |
| 2026-08-25 | 🔵 **EN REVISIÓN**: las **horas de pase** (18/20/22) no encajan con películas de 2h30-3h30. Ver propuesta detallada abajo. | David & Luizay |

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

### ⚠️ Lo que hay que hablar antes de hacerlo

- **Toca `templates/peliculas/nueva_pelicula.html`, que es de Luizay.** De ahí
  que esto esté en revisión y no hecho: conviene acordarlo para no chocar en el
  siguiente merge.
- **La clave de TMDB está en el `.env` de cada equipo.** En un equipo sin `.env`
  el botón fallaría, así que habría que detectarlo y ocultarlo con un aviso
  claro en vez de soltar un error.
- **`DetallePelicula`** (fecha de estreno, clasificación por edad) es otro modelo
  y el formulario actual no lo incluye. TMDB da la fecha de estreno, así que
  podría rellenarse también, pero implica tocar el formulario algo más a fondo.
  ¿Se deja fuera de momento?

### Estado

⬜ Pendiente de que Luizay opine. No se ha escrito nada de código todavía.

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

### Recomendación

La **2**, por sencilla: es cambiar una constante y volver a lanzar
`regenerar_sesiones --borrar`. La 3 queda para cuando el resto esté cerrado.

### Estado

⬜ Pendiente de decidir entre los dos.
