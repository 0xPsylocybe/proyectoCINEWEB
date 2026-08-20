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

## 4. Entidades (tablas) previstas

| App            | Tablas                                                        |
|----------------|--------------------------------------------------------------|
| `peliculas`    | `peliculas`, `directores`, `genero`, `detalle_peliculas`     |
| `cartelera`    | `sala`, `caracteristicas_sala`, `peliculas_en_sala`          |
| `restauracion` | `productos`, `venta_productos`                               |
| `reservas`     | `venta_entradas`                                             |
| `usuarios`     | Roles con grupos/permisos nativos de Django                  |
| `core`         | (sin modelos)                                               |

Relaciones principales previstas:

- `peliculas` — `directores`: una película tiene un director (N:1).
- `peliculas` — `genero`: una película puede tener varios géneros (N:M).
- `peliculas` — `detalle_peliculas`: información ampliada (1:1).
- `peliculas_en_sala` — `peliculas` / `sala`: cada sesión referencia una película y una sala.
- `caracteristicas_sala` — `sala`: una sala tiene varias características (N:M).
- `venta_entradas` — `peliculas_en_sala`: entradas asociadas a una sesión.
- `venta_productos` — `productos`: ventas asociadas a un producto.

---

## 5. Usuarios y permisos

Roles acordados:

- **Sysadmin (superusuario):** acceso total, gestión desde el Django Admin.
- **Gestores (usuarios con permisos):** pueden crear, modificar y eliminar
  cartelera, películas, sesiones, productos, etc. desde la web.
- **Visitantes anónimos:** no necesitan registrarse ni iniciar sesión; pueden
  consultar la cartelera y **comprar entradas y productos de restauración**.

Por tanto, la compra de entradas y de productos es **anónima**: las tablas
`venta_entradas` y `venta_productos` no guardan usuario. El sistema de
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
