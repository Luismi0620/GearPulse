# Integración con el equipo aliado

## Contrato que GearPulse provee

El aliado puede consumir:

```http
GET http://IP_ELASTICA:8080/api/v2/public/summary/
Accept: application/json
```

La respuesta contiene `service`, `version`, `status`, `capabilities` y `contract`. No incluye datos personales.

## Contrato que GearPulse consume

Solicite al equipo aliado un endpoint `GET` público para la sustentación que:

- responda JSON (`object` o `array`);
- use HTTPS cuando esté fuera de la red local;
- responda en menos de cuatro segundos;
- no requiera cookies de navegador;
- permanezca encendido durante la evaluación.

Configure la URL completa en `.env`:

```dotenv
ALLY_SERVICE_URL=https://dominio-del-aliado.example/api/public/summary/
```

Reinicie únicamente el adaptador:

```bash
docker compose up -d --force-recreate integration_service
curl -i http://localhost:8080/api/v2/integrations/ally/
```

Una respuesta correcta se normaliza como:

```json
{
  "source": "allied-team",
  "status": "available",
  "data": {}
}
```

Si el aliado no está configurado o está caído, GearPulse devuelve un error estructurado `503`. El Adapter
usa timeout, reintentos y circuit breaker para que la falla externa no afecte otros flujos.

## Evidencia recomendada

Conserve el acuerdo de integración, una captura de ambos endpoints funcionando, fecha/hora de la prueba y
el commit que añadió la URL solo al entorno EC2. Nunca confirme tokens o credenciales en Git.
