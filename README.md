# 🎬 CINEWEB

Aplicación web para la gestión de la cartelera de un pequeño cine independiente.

**Autores:** Luizay & David
**Stack previsto:** Python · Django · PostgreSQL · Bootstrap

> ⚠️ Estado: **estructura inicial**. Las apps están creadas pero vacías; todavía
> no hay código (modelos, vistas, plantillas...). Este README recoge la fase de
> análisis y el plan de trabajo.

---

## 1. Proyecto — ¿Qué problema resuelve?

Un cine independiente necesita una aplicación web para gestionar su cartelera.
La aplicación permitirá:

- A los **visitantes** (sin registro): consultar las películas disponibles, ver su
  detalle y las sesiones, buscar/filtrar por título y género, y **comprar entradas
  y productos de restauración sin necesidad de iniciar sesión**.
- A los **gestores**: administrar la información (crear, modificar y eliminar
  películas, sesiones, productos, etc.) desde la web, con un sistema de roles y permisos.

---

## 2. Estructura del proyecto

El proyecto Django se llama **`config`**. Estructura actual:

```
proyectoCINEWEB/
├── config/          # Proyecto Django (settings, urls, wsgi, asgi)
├── core/            # Páginas generales/estáticas (inicio, sobre el cine)
├── peliculas/       # Películas, directores, géneros, detalle
├── cartelera/       # Salas, características de sala, sesiones
├── usuarios/        # Autenticación y roles/permisos
├── reservas/        # Venta de entradas
├── restauracion/    # Productos y ventas de restauración
├── manage.py
├── requirements.txt
├── .gitignore
├── PROGRESO.md
└── README.md
```

Pendiente de crear más adelante: `templates/`, `static/` y las migraciones.

---

## 3. Aplicaciones y responsabilidades

| App              | Responsabilidad                                                              |
|------------------|------------------------------------------------------------------------------|
| **core**         | Páginas generales/estáticas: inicio y "Sobre el cine".                       |
| **peliculas**    | Películas, directores, géneros y detalle. CRUD y búsqueda/filtrado.          |
| **cartelera**    | Salas, características de sala y sesiones (proyecciones). Listado y detalle.  |
| **usuarios**     | Autenticación (login/logout) y gestión de roles y permisos.                  |
| **reservas**     | Venta/reserva de entradas para las sesiones.                                 |
| **restauracion** | Productos de restauración y sus ventas.                                      |

---

## 4. Modelos y tablas previstos

**Convención de nombres:** los modelos se definen en **PascalCase singular** y el
nombre de tabla se fija explícitamente con `db_table` en **snake_case singular**.
Las columnas siguen la convención de Django: **PK `id`** en cada tabla y **FK
`<campo>_id`** (p. ej. `director_id`, `pelicula_id`). El esquema lo crean las
**migraciones de Django** (`managed = True`); los triggers y el SQL a medida se
añaden dentro de una migración con `RunSQL`.

| App            | Modelo               | Tabla (`db_table`)     |
|----------------|----------------------|------------------------|
| `peliculas`    | `Pelicula`           | `pelicula`             |
| `peliculas`    | `Director`           | `director`             |
| `peliculas`    | `Genero`             | `genero`               |
| `peliculas`    | `DetallePelicula`    | `detalle_pelicula`     |
| `cartelera`    | `Sala`               | `sala`                 |
| `cartelera`    | `CaracteristicaSala` | `caracteristica_sala`  |
| `cartelera`    | `Sesion`             | `sesion`               |
| `restauracion` | `Producto`           | `producto`             |
| `restauracion` | `VentaProducto`      | `venta_producto`       |
| `reservas`     | `VentaEntrada`       | `venta_entrada`        |
| `usuarios`     | (roles con grupos/permisos de Django) | —     |
| `core`         | (sin modelos)        | —                      |

Relaciones principales previstas:

- `Pelicula` — `Director`: una película tiene un director (N:1).
- `Pelicula` — `Genero`: cada película tiene un género (N:1).
- `Pelicula` — `DetallePelicula`: información ampliada (1:1).
- `Sesion` — `Pelicula` / `Sala`: cada sesión referencia una película y una sala (N:1 con cada una).
- `Sala` — `CaracteristicaSala`: cada sala tiene una característica (N:1).
- `VentaEntrada` — `Pelicula` / `Sala`: cada venta de entrada referencia una película y una sala.
- `VentaProducto` — `Producto`: cada venta referencia un producto.

---

## 5. Usuarios y permisos

Roles acordados:

- **Sysadmin (superusuario):** acceso total, gestión desde el Django Admin.
- **Gestores (usuarios con permisos):** pueden crear, modificar y eliminar
  cartelera, películas, sesiones, productos, etc. desde la web.
- **Visitantes anónimos:** no necesitan registrarse ni iniciar sesión; pueden
  consultar la cartelera y **comprar entradas y productos de restauración**.

Por tanto, la compra de entradas y de productos es **anónima**: las tablas
`venta_entrada` y `venta_producto` no guardan usuario. El sistema de
autenticación de Django (login/logout) se usa solo para **gestores** y **sysadmin**.

> ⚠️ La gestión debe protegerse **a nivel de URL** (login + permisos), no solo
> ocultando botones en la interfaz.

---

## 6. Reparto del trabajo (Luizay & David)

Reparto orientativo por responsabilidades, con revisión cruzada del código.

### 👤 Luizay
- App **core** (plantilla base, navbar, inicio, sobre el cine).
- App **peliculas** (modelos, CRUD, búsqueda por título y filtrado por género).
- **cartelera** (parte de visualización): listado y detalle.

### 👤 David
- App **usuarios** (autenticación, roles y permisos).
- **cartelera** (parte de gestión): salas, características y sesiones.
- App **reservas** (venta de entradas y productos).
- App **restauracion** (productos).
- Lógica de la BBDD (triggers y demás).

### Común
- Configuración del proyecto `config` y del Django Admin.
- Sistema de mensajes, integración, pruebas y README.

---

## 7. Próximos pasos

Estas secciones se completarán cuando exista código:

- Instalación y entorno virtual.
- Dependencias (`requirements.txt`).
- Configuración de PostgreSQL.
- Migraciones.
- Creación de usuarios y configuración de permisos.
- Ejecución del servidor.

algunas anotaciones:
- creé un entorno virtual: para que funcionara tuve que ;
1.Presiona las teclas Ctrl + Shift + P para abrir la paleta de comandos.
2.Escribe y selecciona: Python: Select Interpreter (Python: Seleccionar intérprete).
3.Busca y elige la opción que apunta a tu entorno virtual local: ./venv/bin/python.

- la base de datos esta en supabase: me parecio mejor asi dado que cada quien esta en su ordenador
- no agregue el campo recaudacion, lo agregmos cuando tengamos esa app lista
- superuser admin 123456hola

---

## 8. Progreso de desarrollo (actualizado)

**Estado actual:** En desarrollo activo. Módulos funcionales: películas, cartelera, usuarios, sesiones.

### ✅ Completado

#### **App Películas**
- ✅ Modelos: `Pelicula`, `Director`, `Genero`, `DetallePelicula`
- ✅ CRUD completo con validaciones
- ✅ Carga de datos: 37 películas (15 en cartelera, 22 archivadas)
- ✅ Datos realistas con directores y géneros españoles/internacionales

#### **App Cartelera**
- ✅ Modelos: `Sala` (7 salas con tipos: 2D, 3D, IMAX x2, LASER, 4DX, VIP)
- ✅ Modelo `Sesion` con validaciones de solapamiento
- ✅ Cálculo automático de tiempos: publicidad (15 min) + película + limpieza (20 min)
- ✅ Generación de 749 sesiones: 14 días x horarios variables por día
- ✅ **Nuevo:** Filtrado de sesiones por "día de cine" (12:00-02:59 del día siguiente)
- ✅ **Nuevo:** Selector de fechas dinámico que destaca día seleccionado

#### **App Usuarios**
- ✅ Autenticación (login/logout)
- ✅ Decorator `@gestor_required` para proteger vistas
- ✅ Sistema de roles: Sysadmin, Gestores, Anónimos
- ✅ Template tags personalizados para control de permisos

#### **Gestión de Sesiones (Nuevo)**
- ✅ CRUD completo de sesiones: crear, leer, editar, eliminar
- ✅ Validación de solapamientos a nivel de modelo y formulario
- ✅ **Opción A (Automática):** Comando Django `manage.py regenerar_sesiones`
  - Parámetros: `--dias N` (default 14), `--borrar` (elimina existentes)
  - Distribuye películas round-robin por salas garantizando cobertura
  - Horarios por día: L-J (18,20,22), V (18,20,22,00), S (12,18,20,22,00), D (12,14,18,20,22,00)
- ✅ **Opción C (Manual):** Vista `/cartelera/sesiones/rellenar/`
  - Seleccionar películas (checkboxes)
  - Seleccionar salas (checkboxes)
  - Rango de fechas (inicio/fin)
  - Opción de borrar sesiones existentes
  - Generación automática con click

#### **UI/UX**
- ✅ Detalle de película con tabs (Horarios / Detalles)
- ✅ Selector de fechas con scroll horizontal y highlight del día
- ✅ Sesiones agrupadas por sala en cards interactivas
- ✅ Botón "Comprar" con estados: deshabilitado/habilitado/hover/active
- ✅ Responsive: mobile, tablet, desktop
- ✅ Estilos Bootstrap 5 + CSS personalizado
- ✅ **Nuevo:** Filtrado visual de 54 sesiones por día (en lugar de ~750)

### 🔄 En progreso
- Agrupación final de salas en template (regroup vs diccionario)
- UI de gestión unificada (películas + sesiones) en panel admin

### ⏳ Pendiente
- **App Restauración:** Productos y ventas
- **App Reservas:** Carrito y checkout de entradas
- **Búsqueda avanzada** en películas
- **Sistema de pagos**
- **Reportes y estadísticas**
- **Tests unitarios e integración**

### Datos actuales en BD
- 37 películas (15 en cartelera)
- 7 salas con características reales
- 749 sesiones generadas
- 15+ directores y 10 géneros

### Stack actual
- **Backend:** Python 3.x, Django 5.2
- **Base de datos:** PostgreSQL (Supabase)
- **Frontend:** Bootstrap 5, CSS3, JavaScript vanilla
- **Auth:** Django auth + decorators personalizados
- **Admin:** Django Jazzmin