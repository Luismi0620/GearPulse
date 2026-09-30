# GearPulse - Taller 01 (Refactorizacion Arquitectonica)

> Taller 02: la migración Strangler Pattern, la matriz de decisión, los contratos y las
> instrucciones Docker están documentados en
> [docs/Migracion-a-Microservicios-Strangler-Pattern.md](docs/Migracion-a-Microservicios-Strangler-Pattern.md).

## Taller 02: ejecución con Docker

El proyecto completo se ejecuta con Docker; no hace falta instalar Python, Django ni Flask en
el equipo anfitrión.

```powershell
docker compose up --build -d
docker compose ps
```

Los servicios `db`, `django_web`, `health_metrics_service` y `nginx` deben aparecer en estado
`running` (los dos primeros servicios con health check se muestran como `healthy`). La API queda
disponible en `http://localhost:8080` y el panel provisional en la raíz.

Verificación del microservicio Flask a través de Nginx:

```powershell
Invoke-RestMethod http://localhost:8080/api/v2/health-metrics/user-123/

Invoke-RestMethod -Method Post `
  -Uri http://localhost:8080/api/v2/health-metrics/ `
  -ContentType 'application/json' `
  -Body '{"user_id":"user-123"}'
```

Pruebas por servicio:

```powershell
docker compose exec -T health_metrics_service python -m unittest flask_metrics_service.test_app
docker compose exec -T django_web python manage.py test accounts subscriptions devices
```

`python manage.py test` sin etiquetas intenta descubrir también los tests de Flask dentro del
contenedor Django, que intencionalmente no instala las dependencias del microservicio. Por eso
las pruebas se ejecutan separadas por servicio.

Implementacion inicial de la funcionalidad critica de negocio: **suscripcion para habilitar metricas de salud** en modo simulacion.

## Objetivo alcanzado

Se refactorizo un flujo monolitico hacia una arquitectura desacoplada con:

- Capa de interfaz (Django CBV)
- Capa de aplicacion (Service Layer)
- Capa de dominio (Builder)
- Capa de infraestructura (Factory + adaptadores)
- Inyeccion de dependencias mediante composition root

## Estructura

- `subscriptions/interfaces/`: vistas y rutas HTTP
- `subscriptions/application/`: orquestacion de casos de uso
- `subscriptions/domain/`: entidades, puertos y builder
- `subscriptions/infra/`: repositorio in-memory, notificador y factory
- `subscriptions/dependencies.py`: ensamblaje de dependencias

## Patrones aplicados

- **Builder**: `SubscriptionBuilder` garantiza que la suscripcion sea valida antes de crearse.
- **Factory**: `NotifierFactory` decide `MockNotifier` o `ConsoleNotifier` segun `ENV_TYPE` (`MOCK` o `REAL`).

## Endpoints

### Activar suscripcion

- `POST /subscription/activate/`
- Body JSON:

```json
{
  "user_id": "u-01",
  "plan": "monthly"
}
```

Respuesta `201`:

```json
{
  "user_id": "u-01",
  "plan": "monthly",
  "status": "active"
}
```

### Consultar metricas (simuladas)

- `GET /subscription/<user_id>/metrics/`

Respuesta `200` (si tiene suscripcion activa):

```json
{
  "user_id": "u-01",
  "pulse_bpm": 74,
  "sleep_hours": 7.2,
  "training_load": 61,
  "generated_at": "2026-08-05T19:13:45.117249"
}
```

Respuesta `403` (si no tiene suscripcion activa):

```json
{
  "error": "User has no active subscription"
}
```

## Ejecucion

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar servidor:

```bash
python manage.py runserver
```

3. Ejecutar pruebas:

```bash
python manage.py test
```

## Pruebas incluidas

- Activacion de suscripcion en service
- Bloqueo de metricas sin suscripcion
- Flujo HTTP: activar y luego consultar metricas
- Flujo HTTP: intento de metricas sin suscripcion

---

# GearPulse - Entrega No. 1 (Nucleo de Negocio y API Profesional)

Sobre la base del Taller 01 se agrego el nucleo de negocio y se migro toda la presentacion a
Django REST Framework.

## Modulos nuevos

- **accounts**: registro de usuarios (`User`), requerido por `subscriptions` y `devices`.
- **devices**: emparejamiento de dispositivos (`Device`, patron **Builder**) y registro de
  sesiones de entrenamiento (`WorkoutSession`).

## Cambios sobre `subscriptions`

- Vistas migradas de `django.views.View` a `rest_framework.views.APIView` con serializers.
- Persistencia real en base de datos (antes era un repositorio en memoria); se mantiene el
  repositorio en memoria solo para pruebas unitarias rapidas.
- Nuevo catalogo de planes (`GET /plans/`).
- Nuevos codigos de estado: **404** si el usuario no existe, **409** si ya tiene una
  suscripcion activa.

## Endpoints

| Metodo | Ruta | Descripcion | Codigos |
|---|---|---|---|
| POST | `/users/register/` | Registra un usuario | 201, 400, 409 |
| GET | `/plans/` | Lista el catalogo de planes | 200 |
| POST | `/subscription/activate/` | Activa una suscripcion | 201, 400, 404, 409 |
| GET | `/subscription/<user_id>/metrics/` | Metricas simuladas | 200, 403 |
| POST | `/devices/pair/` | Empareja un dispositivo (Builder) | 201, 400, 404, 409 |
| POST | `/devices/<device_id>/workouts/` | Registra una sesion de entrenamiento | 201, 400, 404 |
| GET | `/devices/<device_id>/workouts/` | Lista sesiones de un dispositivo | 200, 404 |

## Modelo de dominio implementado (6 de 8 clases propuestas, ~60%)

`User`, `Device`, `Subscription`, `Plan`, `HealthMetrics`, `WorkoutSession`. Quedan para una fase
futura `PaymentTransaction` y `Notification` (esta ultima ya existe como el puerto `Notifier`).

Ver `docs/Entrega-01-Nucleo-de-Negocio.md` para la justificacion de carpetas, el diagrama de
secuencia del flujo mas complejo y la vision de escalabilidad hacia un API Gateway.

## Ejecucion

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test
```
