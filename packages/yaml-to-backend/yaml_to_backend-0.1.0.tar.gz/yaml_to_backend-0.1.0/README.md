# YAML-to-Backend - Generador de Backends desde YAML

Una librería Python para generar automáticamente backends asincrónicos completos que crean endpoints RESTful CRUD, autenticación y autorización basada en roles a partir de archivos YAML.

## 🚀 Instalación

```bash
pip install yaml-to-backend
```

## 📦 Uso como librería

```python
from yaml_to_backend import update_config, get_run_backend

# Configurar el backend
update_config(
    DB_HOST='localhost',
    DB_USER='root',
    DB_PASSWORD='1234',
    DB_NAME='mi_db',
    PORT=8001
)

# Ejecutar el backend
run_backend = get_run_backend()
run_backend()
```

## 🖥️ Uso desde línea de comandos

```bash
# Ejecutar con configuración por defecto
yaml-to-backend

# Cambiar puerto
yaml-to-backend --port 8001

# Configurar base de datos
yaml-to-backend --db-host localhost --db-name test --db-user root --db-password 1234

# Especificar ruta de entidades
yaml-to-backend --entities ./mis_entidades/

# Modo debug
yaml-to-backend --debug
```

## 🔐 Publicación Automática

Este proyecto usa **Trusted Publishers** de PyPI para publicación automática:

- ✅ **Sin tokens**: No necesitas manejar credenciales
- ✅ **Automático**: Se publica con cada release de GitHub
- ✅ **Seguro**: Solo se publica desde el repositorio oficial

### Para contribuir:

1. **Fork** el repositorio
2. **Desarrolla** tus cambios
3. **Crea un Pull Request**
4. **Los maintainers** crearán un release
5. **Automáticamente** se publicará en PyPI

## 🚀 Características

- **Generación automática**: Crea backends completos desde archivos YAML
- **Backend asincrónico**: Usa FastAPI y TortoiseORM para máxima performance
- **Autenticación JWT**: Sistema de autenticación seguro con tokens JWT
- **Autorización por roles**: Control de acceso granular por entidad y campo
- **Permisos condicionales**: Soporte para permisos tipo "yo" (solo datos del usuario)
- **Borrado lógico**: Soporte para borrado lógico y físico
- **Pruebas automáticas**: Tests unitarios y de endpoints generados automáticamente
- **Configuración centralizada**: Todo configurable desde `config.py`

## 📋 Requisitos

- Python >= 3.10
- MySQL (configurable)
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación y Configuración

### Opción 1: Instalación desde PyPI (Recomendado)

```bash
pip install yaml-to-backend
```

### Opción 2: Instalación desde desarrollo

```bash
# Clonar el repositorio
git clone <repository-url>
cd IPAS

# Instalar en modo desarrollo
pip install -e .
```

### Configuración

1. **Configurar base de datos**:
   - Crear una base de datos MySQL
   - Configurar credenciales en `main.py` o variables de entorno

2. **Configurar entidades**:
   - Crear archivos YAML en la carpeta `entidades/`
   - Ver ejemplos en `entidades/usuario.yaml` y `entidades/tarea.yaml`

3. **Ejecutar el backend**:
```bash
# Usando el CLI
yaml-to-backend

# O usando Python
python main.py
```

## ⚙️ Configuración

### Variables de entorno

```bash
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=mi_base

# Servidor
DEBUG=True
PORT=8000
INSTALL=True
LOG=True

# Entidades
ENTITIES_PATH=./entidades/

# JWT
JWT_SECRET_KEY=tu_clave_secreta_muy_segura_aqui
```

### Archivo config.py

```python
# Configuración de base de datos
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'mi_base'

# Configuración del servidor
DEBUG = True
PORT = 8000
INSTALL = True
LOG = True

# Configuración de autenticación
AUTH = {
    'tabla': 'usuarios',
    'columna_usuario': 'username',
    'columna_password': 'password',
    'superusuario': 'admin',
    'password_default': 'admin123',
    'columna_borrado': 'deleted_at',
    'borrado_logico': 'timestamp'
}
```

## 📝 Definición de Entidades

### Estructura YAML

```yaml
entidad: NombreEntidad
tabla: nombre_tabla
campos:
  id:
    tipo: integer
    pk: true
  nombre:
    tipo: string
    max: 100
  descripcion:
    tipo: text
  usuario_id:
    tipo: integer
    fk: usuarios.id
  activo:
    tipo: boolean
  fecha_creacion:
    tipo: datetime
permisos:
  admin: [r, w, d]
  usuario:
    yo:
      campo_usuario: usuario_id
```

### Tipos de campos soportados

- `integer` / `int`: Número entero
- `string`: Texto con longitud máxima
- `text`: Texto largo
- `boolean` / `bool`: Valor booleano
- `datetime`: Fecha y hora
- `date`: Solo fecha
- `float`: Número decimal
- `decimal`: Decimal con precisión
- `json`: Datos JSON

### Permisos

- `r`: Lectura
- `w`: Escritura
- `d`: Eliminación
- `yo`: Solo datos del usuario actual
  - Sin configuración: filtra por `id` del usuario
  - Con `campo_usuario`: filtra por campo específico

## 🔐 Autenticación y Autorización

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Respuesta

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Uso de tokens

```http
GET /api/entidades
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 📡 Endpoints Generados

Para cada entidad se generan automáticamente:

```http
GET    /api/entidad/          # Listar todas
POST   /api/entidad/          # Crear nueva
GET    /api/entidad/{id}      # Obtener por ID
PUT    /api/entidad/{id}      # Actualizar
DELETE /api/entidad/{id}      # Eliminar
GET    /api/entidad/yo        # Solo si hay permisos 'yo'
```

## 🧪 Pruebas

### Ejecutar pruebas con el ejecutor integrado

```bash
# Ejecutar todas las pruebas
python tests/run_tests.py all

# Solo pruebas de integración
python tests/run_tests.py integration

# Solo pruebas unitarias
python tests/run_tests.py unit

# Solo pruebas de autenticación
python tests/run_tests.py auth

# Solo pruebas del parser
python tests/run_tests.py parser

# Solo pruebas de endpoints
python tests/run_tests.py endpoints

# Pruebas con cobertura
python tests/run_tests.py coverage

# Ver ayuda
python tests/run_tests.py help
```

### Ejecutar pytest directamente

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Solo pruebas de integración
pytest tests/ -m integration -v

# Solo pruebas unitarias
pytest tests/ -m "not integration" -v

# Solo pruebas de autenticación
pytest tests/test_auth.py

# Solo pruebas de endpoints
pytest tests/test_endpoints.py

# Solo pruebas del parser
pytest tests/test_entity_parser.py

# Con cobertura
pytest tests/ --cov=backend --cov-report=html
```

**Nota**: Para las pruebas de integración, asegúrate de que el backend esté ejecutándose en otra terminal con `python main.py`.

## 📁 Estructura del Proyecto

```
IPAS/
├── main.py                      # Punto de entrada (usa YAML-to-Backend)
├── pyproject.toml              # Configuración del paquete
├── setup.py                    # Configuración de instalación
├── MANIFEST.in                 # Archivos incluidos en el paquete
├── requirements.txt            # Dependencias de desarrollo
├── pytest.ini                 # Configuración de pruebas
├── README.md                  # Documentación
├── Criterio_Aceptacion_Backend.md # Criterios de aceptación
├── yaml_to_backend/                  # Librería YAML-to-Backend (paquete principal)
│   ├── __init__.py            # API pública
│   ├── cli.py                 # Interfaz de línea de comandos
│   ├── app.py                 # Aplicación principal
│   ├── config.py              # Configuración
│   ├── core/                  # Lógica base
│   │   ├── entity_parser.py   # Parser de YAML
│   │   └── model_generator.py # Generador de modelos
│   ├── db/                    # Base de datos
│   │   ├── connection.py      # Conexión DB
│   │   └── models.py          # Modelos base
│   ├── api/                   # Endpoints
│   │   ├── auth_routes.py     # Rutas de auth
│   │   └── crud_generator.py  # Generador CRUD
│   └── security/              # Seguridad
│       └── auth.py            # Autenticación
├── tests/                     # Pruebas
│   ├── conftest.py            # Configuración de pytest
│   ├── run_tests.py           # Ejecutor de pruebas
│   ├── test_auth.py           # Pruebas de auth
│   ├── test_entity_parser.py  # Pruebas del parser
│   ├── test_endpoints.py      # Pruebas unitarias de endpoints
│   ├── test_endpoints_simple.py # Pruebas simples de endpoints
│   ├── test_endpoints_integration.py # Pruebas de integración
│   └── test_endpoints_complete.py # Pruebas completas
└── entidades/                 # Archivos YAML
    ├── usuario.yaml           # Entidad Usuario
    └── tarea.yaml             # Entidad Tarea
```

## 🔄 Modo Instalación

Cuando `INSTALL = True` en la configuración:

1. Se conecta a la base de datos
2. Borra todas las tablas existentes
3. Regenera las tablas desde los YAML
4. Crea usuarios iniciales definidos en `config.py`

### Usuarios iniciales por defecto

- **admin** / **admin123** (rol: admin)
- **usuario1** / **usuario123** (rol: usuario)

## 🚀 Ejemplos de Uso

### 1. Crear una nueva entidad

Crear `entidades/producto.yaml`:

```yaml
entidad: Producto
tabla: productos
campos:
  id:
    tipo: integer
    pk: true
  nombre:
    tipo: string
    max: 100
  precio:
    tipo: float
  categoria_id:
    tipo: integer
    fk: categorias.id
  activo:
    tipo: boolean
permisos:
  admin: [r, w, d]
  vendedor: [r, w]
  cliente: [r]
```

### 2. Usar el endpoint generado

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Crear producto
curl -X POST "http://localhost:8000/api/producto/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop", "precio": 999.99, "activo": true}'
```

## 🔧 Desarrollo

### Agregar nuevas funcionalidades

1. **Nuevos tipos de campo**: Modificar `yaml_to_backend.core.model_generator.ModelGenerator._get_tortoise_field_type()`
2. **Nuevos permisos**: Extender `yaml_to_backend.security.auth.AuthManager.has_permission()`
3. **Nuevos endpoints**: Modificar `yaml_to_backend.api.crud_generator.CRUDGenerator.generate_crud_router()`

### Debugging

Con `DEBUG = True`:
- Logs detallados en consola
- Información de generación de modelos
- Errores detallados

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte y preguntas:
- Crear un issue en GitHub
- Revisar la documentación
- Verificar los logs con `DEBUG = True` 