# 🎬 CINEWEB

Aplicación web para la gestión de la cartelera de un pequeño cine independiente.

**Autores:** Luizay & David
**Stack previsto:** Python · Django · PostgreSQL · Bootstrap

> ✅ Estado: **en desarrollo activo**. Funcionan películas, cartelera, sesiones,
> usuarios, el Snack Bar y la compra de entradas con selección de butacas.
> El detalle del avance está en la sección 8 y en `PROGRESO.md`.

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
| `reservas`     | `EntradaButaca`      | `entrada_butaca`       |
| `reservas`     | `ReservaButaca`      | `reserva_butaca`       |
| `restauracion` | `Categoria`          | `categoria`            |
| `usuarios`     | (roles con grupos/permisos de Django) | —     |
| `core`         | (sin modelos)        | —                      |

> ⚠️ La convención de `db_table` se aplicó en `reservas` y `restauracion`, pero
> los modelos de `peliculas` y `cartelera` se quedaron con el nombre por defecto
> de Django (`peliculas_peliculas`, `cartelera_sesion`, `cartelera_sala`).
> Tenedlo en cuenta al escribir SQL a mano o triggers.

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

## 7. Puesta en marcha

### 7.1 Requisitos

- **Python 3.11 o superior**
- Acceso a la base de datos **PostgreSQL** del proyecto (está en Supabase, así
  no hace falta instalar Postgres en cada equipo)
- Git

### 7.2 Instalación

```bash
git clone https://github.com/0xPsylocybe/proyectoCINEWEB.git
cd proyectoCINEWEB
```

Entorno virtual:

```bash
python -m venv venv
```

Activarlo — **Windows (PowerShell)**:

```bash
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**:

```bash
source venv/bin/activate
```

Dependencias:

```bash
pip install -r requirements.txt
```

> 💡 **En VS Code**, si no reconoce el entorno: `Ctrl+Shift+P` →
> *Python: Select Interpreter* → elegir el de `./venv`.

### 7.3 Variables de entorno

**Este paso es obligatorio: sin él la aplicación no arranca.** Las credenciales
no están en el código, se leen de un fichero `.env` que no se sube al
repositorio, así que **cada equipo necesita el suyo**.

Copia la plantilla:

```bash
copy .env.example .env
```

En macOS o Linux:

```bash
cp .env.example .env
```

Y rellena los valores:

| Variable | Para qué | De dónde sale |
|----------|----------|---------------|
| `DJANGO_SECRET_KEY` | Firma de sesiones y cookies | Se genera (ver abajo) |
| `DJANGO_DEBUG` | Modo desarrollo | `True` en local |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST` | Conexión a Supabase | Pídeselos a tu compañero |
| `TMDB_API_KEY` | Carteles y fichas | Tu cuenta de TMDB (opcional) |

Para generar una `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

La clave de TMDB se saca gratis en
[themoviedb.org/settings/api](https://www.themoviedb.org/settings/api); vale
tanto la *API Key* (v3) como el *Read Access Token* (v4). **Es la única
opcional**: sin ella la aplicación funciona igual, solo que el botón "Buscar en
TMDB" del alta de película no aparece.

Si falta alguna variable, Django avisa al arrancar de cuál es.

### 7.4 Base de datos

El esquema se crea con las migraciones:

```bash
python manage.py migrate
```

Esto incluye el **trigger de recaudación**, que se instala desde la migración
`reservas/0005_trigger_recaudacion`.

> ⚠️ La base de datos es **compartida** entre los dos. Al hacer `migrate` estás
> tocando el esquema que usa también el otro: avisa antes si la migración borra
> o cambia columnas.

### 7.5 Usuario administrador y gestores

```bash
python manage.py createsuperuser
```

Los **gestores** no se registran desde la web: se crean en el Django Admin
(`/admin/`) y se añaden al grupo **`Gestores`**. Un usuario es gestor si es
superusuario o pertenece a ese grupo (ver `usuarios/decorators.py`).

Si el grupo no existe, se crea desde el admin en *Grupos* → *Añadir*, con los
permisos de `peliculas`, `cartelera` y `restauracion`.

### 7.6 Datos de prueba

Los datos ya están cargados en la base compartida. Si hicieran falta de nuevo:

```bash
# Corrige fichas de películas (títulos, directores, sinopsis, duraciones)
python manage.py corregir_peliculas --dry-run    # ensayo, no toca nada
python manage.py corregir_peliculas

# Carteles y fichas desde TMDB (necesita el .env)
python manage.py importar_tmdb --conservar-titulos

# Programación de sesiones de los próximos 14 días
python manage.py regenerar_sesiones --dry-run --borrar   # ensayo
python manage.py regenerar_sesiones --dias 14 --borrar
```

Todos admiten `--dry-run`, que enseña lo que harían sin guardar nada.

> Si las **imágenes salen rotas**, es que a esa película le falta el cartel en
> la BBDD. Se recuperan con:
> `python manage.py importar_tmdb --conservar-titulos --solo-carteles`

### 7.7 Arrancar

```bash
python manage.py runserver
```

La web queda en <http://127.0.0.1:8000/> y el panel en
<http://127.0.0.1:8000/admin/>.

### 7.8 Rutas principales

| Ruta | Qué es | Quién entra |
|------|--------|-------------|
| `/` | Portada | Cualquiera |
| `/cartelera/` | Cartelera y próximos estrenos | Cualquiera |
| `/cartelera/detalle/<id>/` | Detalle de película con sus horarios | Cualquiera |
| `/restauracion/` | Snack Bar | Cualquiera |
| `/reservas/carrito/` | Compra: butacas y productos | Cualquiera |
| `/cartelera/sesiones/` | Gestión de sesiones | Gestores |
| `/peliculas/lista_peliculas` | Gestión de películas | Gestores |
| `/usuarios/` | Acceso de gestores | — |
| `/admin/` | Django Admin | Superusuario |

### 7.9 Sobre las credenciales ⚠️

Hasta el 25/08 la contraseña de Supabase y la `SECRET_KEY` estaban escritas en
`config/settings.py`, que sí se sube al repositorio. Ya no: se leen del `.env`.

**Pero siguen en el historial de Git.** Quitarlas del fichero no las borra de
los commits anteriores, así que cualquiera con acceso al repositorio puede
recuperarlas. Por eso hay que:

1. **Rotar la contraseña** de la base de datos en el panel de Supabase.
2. Generar una **`SECRET_KEY` nueva** (ver 7.3). Ojo: al cambiarla se cierran
   las sesiones abiertas, hay que volver a entrar al admin.
3. Actualizar el `.env` de cada equipo con los valores nuevos.

Y si esto llegara a desplegarse, poner `DJANGO_DEBUG=False` y rellenar
`DJANGO_ALLOWED_HOSTS`.

---

## 8. Progreso de desarrollo (actualizado)

**Estado actual:** En desarrollo activo. Módulos funcionales: películas, cartelera, usuarios, sesiones.

### ✅ Completado

#### **App Películas**
- ✅ Modelos: `Pelicula`, `Director`, `Genero`, `DetallePelicula`
- ✅ CRUD completo con validaciones y subida de póster
- ✅ Alta rápida de **género** y **director** desde el propio listado
- ✅ Catálogo de 35 películas (14 en cartelera, 21 fuera)
- ✅ `Peliculas.recaudacion` — solo lectura en el admin. La mantiene al día un
  **trigger de PostgreSQL** (`reservas/0005_trigger_recaudacion`) por el camino
  `venta_entrada → sesion → pelicula`. Cubre los tres casos: una venta suma,
  una anulación resta, y si se corrige una venta ajusta la diferencia (incluso
  si se cambia a una sesión de otra película). Se hizo con un trigger, y no en
  la vista de compra, para que cuadre venga la venta del formulario, del Django
  Admin o de un `INSERT` a mano. Los productos del Snack Bar **no** cuentan:
  la recaudación es solo taquilla
- ✅ `Peliculas.puntuacion` — nota media sobre 10, la importa `importar_tmdb`.
  ⚠️ Es la puntuación de **TMDB**, no la de IMDb: TMDB no expone la nota de
  IMDb por su API (solo el `imdb_id`); para esa haría falta OMDb y otra clave.
  El campo tiene nombre neutro, así que cambiar de fuente solo afecta al
  importador, no a las vistas ni a las plantillas
- ✅ **Fichas corregidas**: la carga inicial había dejado 8 títulos inventados y
  varios directores mal asignados (*La zona de interés* figuraba como de Nolan,
  *Vidas pasadas* de Chazelle...). Comando `corregir_peliculas`
- ✅ **Carteles**: las 35 películas tienen póster, importado de TMDB junto con
  sinopsis, duración y año. Comando `importar_tmdb`
- ✅ **Botón "Buscar en TMDB"** al dar de alta o editar una película: escribes el
  título, pulsas y se rellenan sinopsis, duración, año, género, director,
  puntuación y el cartel (con vista previa). El gestor revisa antes de guardar.
  Si el equipo no tiene clave de TMDB, el botón simplemente no aparece

##### Comandos de datos

```bash
python manage.py corregir_peliculas --dry-run   # ensayo, no toca nada
python manage.py corregir_peliculas             # aplica las correcciones

python manage.py importar_tmdb --conservar-titulos   # carteles + fichas de TMDB
```

`importar_tmdb` necesita una clave de TMDB en un fichero `.env` de la raíz
(`TMDB_API_KEY=...`, ignorado por git). Acepta tanto la API key v3 como el
token v4. Con `--conservar-titulos` mantiene título, género y director de la
BBDD y solo toma de TMDB el cartel, la sinopsis, la duración y el año.

- ✅ **Los carteles se guardan en la BBDD** (modelo `CartelPelicula`), no solo en
  `media/`. Como la base de datos es compartida y la carpeta `media/` está en
  `.gitignore`, antes las imágenes se veían rotas en el equipo del compañero.
  Se sirven desde `/peliculas/cartel/<id>/` con caché de un día

> El binario va en una tabla aparte a propósito: si estuviera dentro de
> `Peliculas`, cada consulta del catálogo arrastraría varios MB de imágenes.

#### **App Cartelera**
- ✅ Modelos: `Sala` (7 salas con tipos: 2D, 3D, IMAX x2, LASER, 4DX, VIP)
- ✅ Modelo `Sesion` con validaciones de solapamiento
- ✅ Cálculo automático de tiempos: publicidad (15 min) + película + limpieza (20 min)
- ✅ Generación de sesiones: 14 días x horarios variables por día. El generador
  **respeta la ocupación de la sala**: no programa un pase si el anterior aún no
  ha terminado (la duración la calcula el propio modelo `Sesion`). Reparte
  recorriendo día → hora → sala, de modo que ninguna película se queda sin pases
- ✅ **Reglas de programación** en `cartelera/programacion.py`, compartidas por el
  comando y la vista "Rellenar automáticamente":
  - L-V no se abre antes de las **17:00**; matinal solo sábado y domingo
  - Pases cada **2h30** (17:00, 19:30, 22:00), porque cada dos horas solo caben
    películas de hasta 85 min contando publicidad y limpieza
  - Viernes y sábado, último pase a la **1:00**, y ahí **no entran películas de
    más de 2 horas**
  - Las sesiones **con entradas vendidas nunca se borran** al regenerar
- ✅ Filtrado de sesiones por "día de cine" (12:00-02:59 del día siguiente)
- ✅ Selector de fechas dinámico que destaca día seleccionado
- ✅ **Nuevo:** `Sala.precio_entrada` — el precio de la entrada depende de la sala
- ✅ **Nuevo:** `Sala.filas` y `Sala.columnas` — rejilla del mapa de butacas
- ✅ **Nuevo:** Cartelera dividida en dos secciones: **Cartelera** (películas
  marcadas `en_cartelera`) y **Próximos estrenos** (el resto)
- ✅ **Nuevo:** Próximos estrenos ordenados por **puntuación**, de mejor a peor.
  Ambas secciones muestran la nota (⭐) sobre el póster
- ✅ **Nuevo:** `/proximos_estrenos/` usa ya el mismo criterio y el mismo orden
  que la sección de la cartelera

#### **App Usuarios**
- ✅ Autenticación con las vistas genéricas de Django (login/logout)
- ✅ **Recuperación de contraseña** completa (solicitud, enviado, confirmación
  y fin), con plantillas propias
- ✅ Decorator `@gestor_required` para proteger vistas
- ✅ Sistema de roles: Sysadmin, Gestores, Anónimos
- ✅ Template tags personalizados para control de permisos
- ℹ️ **No hay registro público**: los gestores se crean desde el admin y se
  añaden al grupo *Gestores*. La compra es anónima y no requiere cuenta

#### **App Core**
- ✅ Plantilla base con Bootstrap 5, preloader con el logo y diseño responsive
- ✅ Navbar superior (con los accesos de gestión) y sidebar lateral plegable
- ✅ Páginas de inicio, "Sobre el cine" y próximos estrenos

#### **Gestión de Sesiones (Nuevo)**
- ✅ CRUD completo de sesiones: crear, leer, editar, eliminar
- ✅ **Filtros en `/cartelera/sesiones/`**: por película, por sala y por rango de
  fechas, combinables entre sí, con paginación de 24 en 24 que conserva los
  filtros al cambiar de página. Cada tarjeta muestra ya el día y la hora.
  Con 250 sesiones, la pantalla era inmanejable sin esto
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

#### **App Restauración (Snack Bar)**
- ✅ Modelo `Categoria` y FK `categoria` en `Producto`
- ✅ 5 categorías y 29 productos (bebidas, palomitas, golosinas, snacks, chocolate)
- ✅ Catálogo público en `/restauracion/`, con las tarjetas en rejilla irregular

#### **App Reservas (compra de entradas)**
- ✅ `VentaEntrada` referencia la **sesión** (antes iba a película + sala suelta)
- ✅ Flujo en tres pasos: **carrito → confirmación → compra realizada**
- ✅ **Selección de butacas** sobre el mapa de la sala
- ✅ **Reserva temporal de 30 minutos** entre elegir butaca y confirmar:
  - `ReservaButaca` guarda el bloqueo con su fecha de caducidad
  - `UniqueConstraint (sesion, fila, numero)` en `EntradaButaca` y en
    `ReservaButaca`: **la propia BBDD impide vender dos veces la misma butaca**,
    aunque dos personas compren a la vez
  - Los bloqueos caducados se liberan solos al consultar el mapa (sin cron)
  - Si alguien se adelanta, se avisa y se vuelve al mapa; nunca un error 500
- ✅ Productos del Snack Bar añadibles durante la compra de entradas
- ✅ Formulario de pago con validación de tarjeta (algoritmo de Luhn, caducidad
  y CVC). **No se guarda ningún dato de la tarjeta**: no hay pasarela de pago,
  es solo la simulación del proceso
- ✅ **Resguardo de compra** con localizador (`CL-000014`), película, día, hora,
  sala, formato, butacas y el desglose de lo pagado. Se puede imprimir, y el
  CSS de impresión deja solo el resguardo

#### **UI/UX**
- ✅ Detalle de película con tabs (Horarios / Detalles)
- ✅ Selector de fechas con scroll horizontal y highlight del día
- ✅ Sesiones agrupadas por sala en cards interactivas
- ✅ Botón "Comprar" con estados: deshabilitado/habilitado/hover/active
- ✅ Responsive: mobile, tablet, desktop
- ✅ Estilos Bootstrap 5 + CSS personalizado
- ✅ Filtrado visual de las sesiones por día (en lugar de las ~750)
- ✅ **Nuevo:** Mapa de butacas con pantalla, leyenda y estados (libre / tuya /
  ocupada), y cuenta atrás de la reserva en la pantalla de confirmación

### ⏳ Pendiente
- **Snack Bar:** el botón ➕ del catálogo todavía no añade nada al carrito
  (aparcado: es un extra, se hará al final)
- ⚠️ **Rotar la contraseña de Supabase y la `SECRET_KEY`**: ya no están en el
  código, pero sí en el historial de Git (ver 7.9)
- **Búsqueda por título y filtrado por género** en películas (estaba previsto y
  no está implementado)
- **`detalle_pelicula`**: la vista existe pero no tiene URL ni plantilla
- **`templates/restauracion/snack_bar.html`** está vacío y duplica el catálogo
- La **portada** muestra las 35 películas, también las que no están en cartelera
- **Limpieza:** quedan 8 directores sin ninguna película tras corregir las fichas
- **Búsqueda avanzada** en películas
- **Reportes y estadísticas**
- **Tests unitarios e integración**

### Datos actuales en BD
- 35 películas (14 en cartelera, 21 en próximos estrenos), todas con cartel
- 7 salas con precio propio y rejilla de butacas
- 225 sesiones generadas, sin ningún solapamiento
- 38 directores y 13 géneros
- 5 categorías y 29 productos de restauración

### Stack actual
- **Backend:** Python 3.x, Django 5.2
- **Base de datos:** PostgreSQL (Supabase)
- **Frontend:** Bootstrap 5, CSS3, JavaScript vanilla
- **Auth:** Django auth + decorators personalizados
- **Admin:** Django Jazzmin