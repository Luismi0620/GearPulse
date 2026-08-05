# GearPulse - Taller 01 (Refactorizacion Arquitectonica)

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
