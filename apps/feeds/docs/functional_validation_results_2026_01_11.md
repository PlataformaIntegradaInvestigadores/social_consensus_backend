# Validación Funcional y de Rendimiento

**Fecha:** 11 de Enero de 2026
**Objetivo**: Validar tiempos de respuesta de operaciones críticas.
**Muestra**: 25 Iteraciones (Casos de Prueba)

## 1. Operaciones CRUD (Create + Like + Comment)
La prueba simuló el flujo completo de creación e interacción 25 veces consecutivas.
- **Promedio**: 1.7367s
- **Meta**: < 1.2s
- **Estado**: ❌ FAILED
- **Observación**: La latencia promedio subió ligeramente con la carga sostenida (de ~1.4s a ~1.7s), confirmando que la operación síncrona es sensible a la carga.

## 2. Generación de Feed Personalizado
Se solicitaron feeds personalizados para el usuario de prueba 25 veces.
- **Promedio**: 0.0058s
- **Meta**: < 1.8s
- **Estado**: ✅ PASSED
- **Observación**: Rendimiento excelente, muy por debajo del límite permitido.

## Conclusión
**EL RENDIMIENTO DE LECTURA (FEED) ES ÓPTIMO, PERO LA ESCRITURA (CRUD) REQUIERE OPTIMIZACIÓN (ASYNC) PARA CUMPLIR LA META DE 1.2s.**
