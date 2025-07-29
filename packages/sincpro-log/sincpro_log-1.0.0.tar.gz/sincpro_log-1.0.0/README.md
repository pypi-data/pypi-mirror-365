# SincPro Logger

Biblioteca de logging estructurado para aplicaciones SincPro, construida sobre `structlog` con capacidades avanzadas de registro.

## Características principales

- **Logging estructurado**: formatos JSON (producción) y consola con colores (desarrollo)
- **Integración con Grafana Loki**: envío de logs para centralización y alertas
- **Contexto enriquecido**: bind/unbind de datos contextuales
- **Tipado seguro**: interfaces completamente tipadas para Python 3.12+

## 🚀 Optimizado para Kubernetes y Observabilidad

**Sincpro Logger** está especialmente diseñado para aplicaciones containerizadas y sistemas de observabilidad modernos:

### Integración con Kubernetes
- **Formato JSON nativo**: Compatible directamente con FluentD, FluentBit y otros log aggregators
- **Metadatos estructurados**: Facilita la correlación de logs entre pods y servicios
- **Context propagation**: Soporte nativo para trace_id y request_id en microservicios
- **Resource labeling**: Etiquetas automáticas para namespace, pod, container

### Sistemas de Observabilidad
- **Grafana Loki**: Integración directa con push automático y etiquetas dinámicas
- **OpenTelemetry ready**: Compatible con estándares de trazabilidad distribuida
- **Structured queries**: Logs optimizados para consultas en Grafana, Kibana y DataDog
- **Alerting support**: Campos estructurados para configuración de alertas automáticas

### Beneficios en Contenedores
```python
# Configuración típica para Kubernetes
logger = create_logger(
    "payment-service",
    namespace="production",
    pod_name=os.getenv("HOSTNAME"),
    version=os.getenv("APP_VERSION", "unknown")
)

# Context tracing automático para microservicios
with logger.tracing() as traced_logger:
    traced_logger.info("Processing payment", amount=100.50)
    # trace_id y request_id se propagan automáticamente
```

## Instalación rápida

```bash
pip install sincpro-logger
# o con Poetry
poetry add sincpro-logger
```

## 📋 Configuración inicial

**⚠️ IMPORTANTE**: La configuración del logger debe ser lo **primero** que se haga en tu aplicación, antes de cualquier import o uso de logging.

### 1. Configuración global del sistema de logging

```python
from sincpro_log import configure_global_logging

# Para desarrollo (formato legible con colores)
configure_global_logging(level="DEBUG")

# Para producción (formato JSON estructurado)
configure_global_logging(level="INFO")
```

### 2. Configuración típica en main.py o app.py

```python
# main.py
import os
from sincpro_log import configure_global_logging, create_logger


def setup_logging():
    """Configurar logging según el entorno."""
    # Detectar entorno
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        configure_global_logging(level="INFO")  # JSON estructurado
    else:
        configure_global_logging(level="DEBUG")  # Formato legible

    return environment


def main():
    # PASO 1: Configurar logging ANTES que todo
    env = setup_logging()

    # PASO 2: Crear logger de la aplicación
    logger = create_logger(
        "mi-aplicacion",
        environment=env,
        version=os.getenv("APP_VERSION", "unknown")
    )

    logger.info("Aplicación iniciada", environment=env)

    # Resto de la aplicación...


if __name__ == "__main__":
    main()
```

## 🏗️ Creación y uso de loggers

### Creación básica

```python
from sincpro_log import create_logger

# Logger básico
logger = create_logger("mi-app")

# Logger con contexto inicial
logger = create_logger(
    "payment-service",
    environment="production",
    version="1.2.3",
    component="api"
)
```

### Añadir y remover contexto persistente

```python
# Añadir campos que persisten en todos los logs
logger.bind(user_id="12345", session_id="abc-def")
logger.info("Usuario autenticado")  # Incluirá user_id y session_id

# Remover campos específicos
logger.unbind("session_id")
logger.info("Sesión terminada")  # Solo incluirá user_id

# Contexto temporal (solo dentro del bloque)
with logger.context(operation="payment", amount=100.50) as temp_logger:
    temp_logger.info("Iniciando pago")  # Incluye operation y amount
    temp_logger.error("Error en pago")  # Incluye operation y amount

logger.info("Pago finalizado")  # NO incluye operation ni amount
```

### Niveles de logging disponibles

```python
logger.debug("Información de depuración")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error controlado")
logger.critical("Error crítico")
logger.exception("Error con stack trace")  # Usar dentro de except
```

## 🔍 Trazabilidad: trace_id y request_id

### ¿Qué son y cuándo usarlos?

- **`trace_id`**: Identificador único que sigue una operación completa a través de múltiples servicios
- **`request_id`**: Identificador único para una petición HTTP específica

**Casos de uso típicos:**
- **Microservicios**: Rastrear una operación que pasa por varios servicios
- **APIs REST**: Asociar todos los logs de una petición HTTP
- **Procesamiento asíncrono**: Seguir trabajos en background
- **Debugging**: Correlacionar logs relacionados en sistemas distribuidos

### Uso con IDs existentes (recibidos)

```python
# Escenario: Recibir trace_id de otro servicio
incoming_trace_id = request.headers.get("X-Trace-ID")
incoming_request_id = request.headers.get("X-Request-ID")

# Usar IDs existentes
with logger.tracing(trace_id=incoming_trace_id, request_id=incoming_request_id) as traced_logger:
    traced_logger.info("Procesando petición de otro servicio")
    # Todos los logs tendrán estos IDs específicos
```

### Uso con IDs auto-generados (cuando no existen)

```python
# Generar automáticamente si no se proporcionan
with logger.tracing() as traced_logger:
    traced_logger.info("Nueva operación iniciada")
    # Se generan automáticamente trace_id y request_id únicos
    
    # Obtener los IDs generados para enviar a otros servicios
    current_trace = traced_logger.get_current_trace_id()
    current_request = traced_logger.get_current_request_id()
    
    # Propagar a servicios downstream
    headers = traced_logger.get_traceability_headers()
    # headers = {"X-Trace-ID": "...", "X-Request-ID": "..."}
```

### Context managers individuales

```python
# Solo trace_id
with logger.trace_id("existing-trace-123") as traced_logger:
    traced_logger.info("Operación con trace específico")

# Solo request_id
with logger.request_id() as request_logger:  # Auto-genera si no se especifica
    request_logger.info("Petición con ID único")

# Combinados
with logger.trace_id("trace-abc") as tl:
    with tl.request_id("request-xyz") as full_logger:
        full_logger.info("Con ambos IDs específicos")
```

### Integración con frameworks web

```python
# Flask
from flask import request

@app.before_request
def setup_request_logging():
    trace_id = request.headers.get("X-Trace-ID")
    request_id = request.headers.get("X-Request-ID")
    
    g.logger = logger.tracing(trace_id=trace_id, request_id=request_id).__enter__()

# FastAPI
from fastapi import Request

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID")
    request_id = request.headers.get("X-Request-ID")
    
    with logger.tracing(trace_id=trace_id, request_id=request_id) as request_logger:
        request.state.logger = request_logger
        response = await call_next(request)
        return response
```

### Propagar metadatos entre servicios

```python
# Servicio A: Enviar petición a Servicio B
with logger.tracing() as traced_logger:
    traced_logger.info("Llamando al servicio de pagos")
    
    # Obtener headers para propagación
    headers = traced_logger.get_traceability_headers()
    
    # Hacer petición HTTP con headers de trazabilidad
    response = requests.post(
        "https://payment-service/process",
        json={"amount": 100.50},
        headers=headers  # {"X-Trace-ID": "...", "X-Request-ID": "..."}
    )
    
    traced_logger.info("Respuesta del servicio de pagos", status=response.status_code)

# Servicio B: Recibir y usar los IDs
def process_payment(request):
    # Extraer IDs del request
    trace_id = request.headers.get("X-Trace-ID")
    request_id = request.headers.get("X-Request-ID")
    
    # Usar los IDs recibidos
    with logger.tracing(trace_id=trace_id, request_id=request_id) as payment_logger:
        payment_logger.info("Procesando pago recibido")
        # Todos los logs mantendrán la trazabilidad original
```

### Ejemplo completo: E-commerce checkout

```python
def checkout_process(user_id: str, cart_items: list):
    """Proceso completo de checkout con trazabilidad."""
    
    # Iniciar nueva transacción
    with logger.tracing() as checkout_logger:
        checkout_logger.info(
            "Iniciando checkout",
            user_id=user_id,
            items_count=len(cart_items)
        )
        
        try:
            # Validar inventario
            with checkout_logger.context(step="inventory_check") as step_logger:
                step_logger.info("Verificando inventario")
                # validate_inventory(cart_items)
                step_logger.info("Inventario validado")
            
            # Procesar pago (enviar a servicio externo)
            payment_headers = checkout_logger.get_traceability_headers()
            with checkout_logger.context(step="payment") as payment_logger:
                payment_logger.info("Procesando pago")
                # payment_response = call_payment_service(headers=payment_headers)
                payment_logger.info("Pago procesado exitosamente")
            
            # Actualizar inventario
            with checkout_logger.context(step="inventory_update") as inv_logger:
                inv_logger.info("Actualizando inventario")
                # update_inventory(cart_items)
                inv_logger.info("Inventario actualizado")
            
            checkout_logger.info("Checkout completado exitosamente")
            
        except Exception as e:
            checkout_logger.exception("Error en checkout", error_step="unknown")
            raise
```

## Arquitectura

Diseñado con Clean Architecture (Domain-Driven Design):
- **Dominio**: Modelos y entidades centrales
- **Casos de uso**: Lógica de negocio para logs
- **Infraestructura**: Integración con servicios externos

## Licencia

Copyright © 2024 Sincpro S.R.L. Todos los derechos reservados.
