# Pruebas y guion de sustentación

## Validación automática

```powershell
python -m unittest discover -s services -p "test_*.py"
python -m unittest flask_metrics_service.test_app
python manage.py test
docker compose config --quiet
```

## Flujo de extremo a extremo

1. Abra la raíz del gateway y cambie entre español e inglés.
2. Registre un usuario y conserve el UUID autocompletado.
3. Active un plan; explique que subscriptions valida al usuario por HTTP.
4. Consulte métricas; explique que metrics valida la suscripción por otro contrato HTTP.
5. Empareje un dispositivo y registre un entrenamiento.
6. Muestre logs del worker: `docker compose logs --tail=50 celery_worker`.
7. Consulte Open-Meteo y señale `WeatherPort`/`OpenMeteoAdapter`.
8. Consulte el aliado y explique la capa anticorrupción y el circuit breaker.
9. Abra `/api/v2/public/summary/` como servicio que GearPulse provee.
10. Muestre `docker compose ps`: gateway, servicios, bases y broker saludables.

## Demostración de exención

1. Abra `gearpulse_project/urls.py` y muestre que Django no registra APIs de negocio.
2. Abra `nginx/nginx.conf` y recorra las rutas Flask.
3. Presente la tabla 7/7 de `docs/ENTREGA-02.md`.
4. Muestre que cada dominio tiene Dockerfile, pruebas y, donde aplica, base propia.
5. Ejecute una prueba de cada servicio para demostrar independencia.

## Evidencia antes de subir

- [ ] Todas las correcciones de E1 están cerradas y vinculadas a commits.
- [ ] Cada estudiante tiene commits propios.
- [ ] La rama evaluable es `main`.
- [ ] La IP elástica responde desde una red externa.
- [ ] `ALLY_SERVICE_URL` apunta al servicio real.
- [ ] EC2 estará encendida durante la sustentación.
- [ ] No hay secretos, `.env` ni llaves `.pem` en Git.
