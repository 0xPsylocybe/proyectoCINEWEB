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
|       | App **core**: plantilla base, navbar, inicio, sobre el cine | 🟡| |
|       | App **peliculas**: modelos (`Pelicula`, `Director`, `Genero`, `DetallePelicula`) | 🟡| |
|       | App **peliculas**: CRUD, búsqueda por título y filtrado por género | 🟡 | |
|       | **cartelera** (visualización): listado y detalle de película | 🟡 | |

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
| 2026-08-25 | *Próximos estrenos* = todas las películas que **no** estén en cartelera (sin mirar la fecha de estreno). ⚠️ La página `/proximos_estrenos/` del menú aún usa el criterio antiguo (no en cartelera **y** fecha futura) y sale vacía: **falta unificar**. | David |
| 2026-08-25 | Los **carteles** no se versionan (`media/` está en `.gitignore`): cada uno los genera con `importar_tmdb`. | David |
