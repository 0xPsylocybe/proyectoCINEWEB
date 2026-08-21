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
|       | App **core**: plantilla base, navbar, inicio, sobre el cine | ⬜ | |
|       | App **peliculas**: modelos (`Pelicula`, `Director`, `Genero`, `DetallePelicula`) | ⬜ | |
|       | App **peliculas**: CRUD, búsqueda por título y filtrado por género | ⬜ | |
|       | **cartelera** (visualización): listado y detalle de película | ⬜ | |

## Progreso — David

| Fecha | Tarea | Estado | Notas / validación |
|-------|-------|--------|--------------------|
|       | App **usuarios**: autenticación (login/logout) | ⬜ | |
|       | App **usuarios**: roles y permisos (grupos Usuario/Gestor) | ⬜ | |
| 2026-08-21 | **cartelera** (gestión): modelos `Sala`, `CaracteristicaSala`, `Sesion` + admin | 🔵 | Modelos y admin escritos; pendiente `migrate` |
| 2026-08-21 | App **reservas**: modelo `VentaEntrada` + admin (falta vistas/compra) | 🟡 | Modelo y admin hechos |
| 2026-08-21 | App **restauracion**: modelos `Producto`/`VentaProducto` + admin (faltan vistas) | 🟡 | Modelos y admin hechos |
|       | Lógica de la BBDD (triggers y demás) | ⬜ | |

---

## Próximos puntos a trabajar

Orden sugerido (de la base hacia arriba). Marcad con quién lo coge y su estado.

### 🔧 Configuración base (común)
1. 🔵 Registrar las 6 apps en `INSTALLED_APPS` (`config/settings.py`).
2. 🔵 Configurar la conexión a **PostgreSQL** en `settings.py` (vía variables de entorno).
3. 🔵 Ajustes de localización (`LANGUAGE_CODE = es-es`, `TIME_ZONE = Europe/Madrid`).
4. 🟡 Crear `templates/` en raíz (subcarpetas por app) y enlazarla en `settings.py` — hecho; falta `static/`.

### 🗄️ Modelos y base de datos
5. 🟡 Definir los modelos según el esquema (con `db_table`; PK `id`, FK `<campo>_id`). — hechos cartelera/reservas/restauración; faltan los de `peliculas` (Luizay).
6. ⬜ `makemigrations` + `migrate` para crear el esquema; triggers/SQL a medida en una migración `RunSQL`. — bloqueado hasta tener los modelos de `peliculas`.
7. 🟡 Registrar los modelos en el **Django Admin**. — hecho para cartelera/reservas/restauración; falta `peliculas`.
8. ⬜ Crear superusuario y datos de prueba.

### 🌐 URLs, vistas y plantillas
9. ⬜ URLs modulares por app con `include()` y `app_name`.
10. ⬜ Plantilla base con Bootstrap (navbar según estado del usuario).
11. ⬜ Página de **cartelera** (cards con datos del ORM).
12. ⬜ Página de **detalle** de película.
13. ⬜ **Búsqueda** por título y **filtrado** por género (ORM).

### 🔐 Usuarios y permisos
> Decisión: **sysadmin** + **gestores** (con permisos) + **visitantes anónimos**.
> La compra de entradas y productos es anónima (sin login). El login es solo para
> gestores/sysadmin.
14. ⬜ Login / logout con el sistema de auth de Django (para gestores/sysadmin).
15. ⬜ Grupo de **gestores** con permisos para gestionar cartelera/películas/productos.
16. ⬜ Proteger vistas de gestión a nivel de URL (no solo ocultando botones).
17. ⬜ Permitir compra de entradas y productos **sin iniciar sesión** (anónima).

### ✏️ Gestión (CRUD)
18. ⬜ CRUD de **películas** (formularios de Django).
19. ⬜ CRUD de **sesiones** (`Sesion`).
20. ⬜ Mensajes de Django (creado / editado / eliminado / error).

### ✅ Cierre
21. ⬜ Completar el README (instalación, BBDD, migraciones, permisos, ejecución).
22. ⬜ Pruebas de instalación desde cero siguiendo el README.
23. ⬜ Revisión cruzada del código del compañero.

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
