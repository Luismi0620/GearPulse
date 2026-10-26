# Despliegue paso a paso en AWS Academy

Estos pasos son externos al repositorio porque requieren acceso al Learner Lab del equipo.

## 1. Preparar AWS Academy

1. Ingrese a AWS Academy, abra el Learner Lab y pulse **Start Lab**.
2. Abra la consola AWS y cree una instancia EC2 Ubuntu Server 24.04 LTS `t3.medium` o superior. El conjunto
   de contenedores usa tres PostgreSQL, Redis, Celery, Nginx, Django y cinco APIs; `t2.micro` puede quedarse
   sin memoria.
3. Cree o seleccione una llave `.pem` y guárdela de forma segura. No la suba al repositorio.
4. En el Security Group permita:
   - SSH TCP 22 solo desde la IP pública del equipo.
   - Custom TCP 8080 desde `0.0.0.0/0` para la demostración.
   - No abra 5432, 6379, 5000 ni 8000.
5. En **Elastic IP addresses**, reserve una dirección y asóciela a la instancia. Registre esa IP para la entrega.

## 2. Instalar Docker en EC2

Conéctese por SSH y ejecute:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Cierre la sesión SSH y vuelva a entrar para aplicar el grupo `docker`. Valide con `docker version` y
`docker compose version`.

## 3. Publicar y clonar la versión evaluable

El PDF exige entregar la rama `main`. Antes del despliegue, integre `entrega2` mediante Pull Request y
asegure que cada integrante tenga commits propios.

```bash
git clone https://github.com/Luismi0620/GearPulse.git
cd GearPulse
git switch main
git pull --ff-only origin main
```

## 4. Configurar secretos e integración aliada

```bash
cp .env.example .env
nano .env
```

Cambie obligatoriamente:

- `POSTGRES_PASSWORD`: contraseña aleatoria larga.
- `DJANGO_SECRET_KEY`: valor aleatorio de al menos 50 caracteres.
- `DJANGO_ALLOWED_HOSTS`: incluya la IP elástica sin protocolo ni puerto.
- `ALLY_SERVICE_URL`: endpoint JSON real acordado con el equipo aliado.

No publique `.env`; está ignorado por Git.

## 5. Construir y arrancar

```bash
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 nginx accounts_service subscriptions_service activity_service health_metrics_service integration_service async_api celery_worker
```

Todos los servicios con health check deben aparecer como `healthy`. Abra:

```text
http://IP_ELASTICA:8080/
```

## 6. Validar la sustentación

```bash
curl -fsS http://localhost:8080/health/
curl -fsS http://localhost:8080/api/v2/public/summary/
curl -fsS http://localhost:8080/api/v2/plans/
curl -fsS 'http://localhost:8080/api/v2/integrations/weather/?latitude=6.2442&longitude=-75.5812'
curl -fsS http://localhost:8080/api/v2/integrations/ally/
docker compose exec -T celery_worker celery -A services.async_service.celery_app.celery inspect ping
```

Cambie el idioma desde la cabecera y complete el flujo usuario -> suscripción -> dispositivo -> entrenamiento
-> métricas. Conserve capturas de `docker compose ps`, del flujo y de los endpoints aliado/externo.

## 7. Operación durante la evaluación

- Inicie el Learner Lab y confirme que EC2 esté `running` al menos 20 minutos antes.
- Verifique que la Elastic IP siga asociada.
- Ejecute `docker compose ps` y reinicie con `docker compose up -d` si fuera necesario.
- No ejecute `docker compose down -v`: `-v` elimina las bases persistentes.
- Entregue el enlace GitHub de `main` y `http://IP_ELASTICA:8080`.

## 8. Actualizaciones posteriores

```bash
git pull --ff-only origin main
docker compose up --build -d
docker image prune -f
```
