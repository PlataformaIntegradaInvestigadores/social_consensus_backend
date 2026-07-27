# Reporte de Pruebas de Rendimiento: Embeddings Microservice

**Fecha:** 11 de Enero de 2026
**Contexto**: Verificación de latencia y disponibilidad del microservicio de embeddings corriendo en Docker.

## Resumen de Ejecución
Se ejecutó el comando `benchmark_embeddings` con 3 iteraciones para validar la conectividad y respuesta del servicio.

> [!NOTE]
> La primera iteración presenta una latencia alta debida al "Cold Start" (carga de modelos en memoria del microservicio). Las iteraciones subsiguientes reflejan el rendimiento real en caliente.

## Resultados Detallados

### 1. Textos Cortos (<100 caracteres)
Simulación de posts cortos o comentarios.

*   **Tasa de Éxito**: 100.0%
*   **Tiempo Promedio (Global)**: 1511.25ms (sesgado por cold start)
*   **Rendimiento en Caliente**: ~300ms - 590ms

**Traza:**
- Iteración 1: `3639.10ms` (Cold Start)
- Iteración 2: `302.70ms`
- Iteración 3: `591.93ms`

### 2. Textos Largos (~6800 caracteres)
Simulación de análisis de documentos o artículos extensos.

*   **Tasa de Éxito**: 100.0%
*   **Tiempo Promedio**: 353.99ms !!!
*   **Estabilidad**: Excelente (variación mínima)

**Traza:**
- Iteración 1: `383.79ms`
- Iteración 2: `340.66ms`
- Iteración 3: `337.51ms`

## Conclusión Técnica
El microservicio está operando con un rendimiento **excepcional** para textos largos, procesando casi 7000 caracteres en menos de 400ms. Esto sugiere que el modelo está optimizado para procesamiento por lotes o que la tokenización es muy eficiente.

El rendimiento cumple y supera los requisitos para operación en tiempo real, aunque se recomienda mantener la estrategia de procesamiento asíncrono para garantizar la escalabilidad bajo carga masiva.
