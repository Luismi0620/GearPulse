# GearPulse

## Entrega No. 1: Núcleo de negocio y API

GearPulse es una API para centralizar el registro de usuarios, la gestión de suscripciones, el
emparejamiento de dispositivos deportivos y el seguimiento de sesiones de entrenamiento. La
aplicación está construida con Django y Django REST Framework, con una separación clara entre
las capas de interfaz, aplicación, dominio e infraestructura.

## Funcionalidades incluidas

- Registro de usuarios con los roles de atleta y administrador.
- Catálogo de planes y activación de suscripciones.
- Consulta de métricas de salud simuladas para usuarios suscritos.
- Emparejamiento de dispositivos mediante el patrón Builder.
- Registro y consulta de sesiones de entrenamiento.

## Arquitectura

El proyecto conserva los siguientes límites por responsabilidad:

- `accounts/`: registro y persistencia de usuarios.
- `subscriptions/`: planes, suscripciones y métricas de salud.
- `devices/`: dispositivos y sesiones de entrenamiento.
- `common/`: excepciones compartidas.
- `gearpulse_project/`: configuración y rutas principales de Django.

En los módulos de dominio se aplican los patrones Builder y Factory. Las vistas REST validan las
solicitudes con serializers y delegan los casos de uso a servicios de aplicación.

## Endpoints

| Método | Ruta | Descripción | Respuestas |
| --- | --- | --- | --- |
| POST | `/users/register/` | Registra un usuario | 201, 400, 409 |
| GET | `/plans/` | Lista el catálogo de planes | 200 |
| POST | `/subscription/activate/` | Activa una suscripción | 201, 400, 404, 409 |
| GET | `/subscription/<user_id>/metrics/` | Consulta métricas simuladas | 200, 403 |
| POST | `/devices/pair/` | Empareja un dispositivo | 201, 400, 404, 409 |
| POST | `/devices/<device_id>/workouts/` | Registra una sesión de entrenamiento | 201, 400, 404 |
| GET | `/devices/<device_id>/workouts/` | Lista las sesiones de un dispositivo | 200, 404 |

### Ejemplo: registrar un usuario

```json
POST /users/register/
{
  "email": "ana@ejemplo.com",
  "role": "athlete"
}
```

Respuesta `201`:

```json
{
  "id": "<uuid>",
  "email": "ana@ejemplo.com",
  "role": "athlete"
}
```

## Ejecución local

Requisitos: Python 3.12 o superior y `pip`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La API estará disponible en `http://127.0.0.1:8000/`.

## Pruebas

```powershell
python manage.py test accounts subscriptions devices
```

Las pruebas cubren el registro de usuarios, la activación de suscripciones, el acceso a métricas,
el emparejamiento de dispositivos y el registro de sesiones de entrenamiento.

## Documentación adicional

La justificación de la estructura de carpetas, el diagrama de secuencia del flujo principal y las
decisiones de diseño de esta entrega se encuentran en
[`docs/Entrega-01-Nucleo-de-Negocio.md`](docs/Entrega-01-Nucleo-de-Negocio.md).
