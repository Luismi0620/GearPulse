# GearPulse - Entrega 2

Evolución de GearPulse a una arquitectura de microservicios desplegable en AWS Academy. Nginx funciona
como API Gateway, Django sirve exclusivamente la interfaz bilingüe y la lógica de negocio se ejecuta en
microservicios Flask independientes. Redis y Celery procesan notificaciones e informes en segundo plano.

## Evidencia para la exención del Parcial 02

La arquitectura desplegada migra **7 de 7 flujos de negocio (100 %)** a servicios independientes, por encima
del 70 % exigido. Django ya no registra rutas de negocio; solo entrega la UI y el selector de idioma.

| Flujo | Propietario en Entrega 2 | Persistencia |
| --- | --- | --- |
| Registro y consulta de usuario | `accounts_service` (Flask) | PostgreSQL accounts |
| Catálogo y activación de planes | `subscriptions_service` (Flask) | PostgreSQL subscriptions |
| Emparejamiento de dispositivos | `activity_service` (Flask) | PostgreSQL activity |
| Registro y consulta de entrenamientos | `activity_service` (Flask) | PostgreSQL activity |
| Métricas de salud | `health_metrics_service` (Flask) | Stateless |
| API externa y equipo aliado | `integration_service` (Flask + Adapter) | Stateless |
| Notificaciones e informes | `async_service` (Flask + Celery) | Redis |

La trazabilidad completa está en [`docs/ENTREGA-02.md`](docs/ENTREGA-02.md).

## Ejecutar todo el ecosistema

Requisitos: Docker Engine con Docker Compose v2.

```powershell
Copy-Item .env.example .env
# Edite .env y configure secretos, host e integración aliada.
docker compose config
docker compose up --build -d
docker compose ps
```

Abra `http://localhost:8080`. Solo Nginx publica un puerto; bases, Redis y servicios permanecen en la red
interna de Docker.

Detener sin borrar datos:

```powershell
docker compose down
```

## Rutas públicas principales

| Método | Ruta | Destino |
| --- | --- | --- |
| POST | `/api/v2/users/register/` | Cuentas |
| GET | `/api/v2/plans/` | Suscripciones |
| POST | `/api/v2/subscriptions/activate/` | Suscripciones |
| POST | `/api/v2/devices/pair/` | Actividad |
| GET/POST | `/api/v2/devices/{id}/workouts/` | Actividad |
| GET | `/api/v2/health-metrics/{user_id}/` | Métricas |
| GET | `/api/v2/integrations/weather/` | API externa vía Adapter |
| GET | `/api/v2/integrations/ally/` | Servicio aliado vía Adapter |
| GET | `/api/v2/public/summary/` | Servicio JSON provisto por GearPulse |
| GET | `/api/v2/tasks/{task_id}/` | Estado de tarea asíncrona |

El contrato completo está en [`docs/openapi.yaml`](docs/openapi.yaml).

## Pruebas

Las pruebas unitarias usan SQLite/memoria y no requieren servicios externos:

```powershell
python -m unittest discover -s services -p "test_*.py"
python -m unittest flask_metrics_service.test_app
python manage.py test
docker compose config --quiet
```

Prueba de humo integral después de levantar Compose:

```powershell
Invoke-RestMethod http://localhost:8080/api/v2/public/summary/
Invoke-RestMethod http://localhost:8080/api/v2/plans/
Invoke-RestMethod 'http://localhost:8080/api/v2/integrations/weather/?latitude=6.2442&longitude=-75.5812'
```

## Documentación de entrega

- [`docs/ENTREGA-02.md`](docs/ENTREGA-02.md): rúbrica, decisiones, diagramas y cálculo de migración.
- [`docs/AWS-ACADEMY-DEPLOYMENT.md`](docs/AWS-ACADEMY-DEPLOYMENT.md): despliegue EC2 e IP elástica paso a paso.
- [`docs/ALLY-SERVICE.md`](docs/ALLY-SERVICE.md): contrato y configuración con el equipo aliado.
- [`docs/CORRECCIONES-ENTREGA-1.md`](docs/CORRECCIONES-ENTREGA-1.md): evidencia y cierre obligatorio de observaciones previas.
- [`docs/PRUEBAS-Y-SUSTENTACION.md`](docs/PRUEBAS-Y-SUSTENTACION.md): guion reproducible de validación.

> Importante: el PDF exige entregar el enlace de la rama `main`, tener la EC2 encendida durante la
> sustentación y que cada estudiante aporte commits identificables.
