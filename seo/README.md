# Seguimiento SEO — Aláez Procurador

Este sistema prepara **informes de oportunidades SEO** sin publicar automáticamente páginas ni escritos. El flujo se ejecuta los lunes a las 07:00 UTC y también manualmente en **GitHub → Actions → Seguimiento SEO Search Console → Run workflow**.

## Conectar Google Search Console

1. En Google Cloud, habilitar **Search Console API** y crear una **cuenta de servicio** de acceso exclusivo a lectura.
2. En Search Console, añadir el correo de esa cuenta de servicio como usuario de la propiedad exacta `https://alaezprocurador.github.io/procurador-leon/` (si la propiedad está registrada de otro modo, adaptar `GSC_PROPERTY`).
3. En GitHub → Settings → Secrets and variables → Actions, crear el secreto **GSC_SERVICE_ACCOUNT_JSON** con el JSON de la cuenta de servicio. **Nunca subir ese JSON al repositorio.**
4. Ejecutar manualmente el flujo y descargar el artefacto `informe-seo` en la ejecución de Actions.
5. Revisar las consultas propuestas, la intención de búsqueda y la exactitud jurídica antes de aprobar contenido.

Si todavía no hay permisos para la API, puede exportarse desde Search Console un CSV de **Consultas** y analizarlo localmente:

```bash
GSC_CSV=/ruta/consultas.csv python scripts/informe_seo.py
```

El script reconoce cabeceras en español e inglés (Consultas/Query, Impresiones/Impressions, Clics/Clicks, CTR y Posición/Position). El informe se guarda en `seo/informes/ultimo-informe.md`. **No subir CSV con información sensible.**

## Política editorial

- Priorizar búsquedas relacionadas con procurador en León y actuaciones de representación procesal.
- Revisar primero las páginas existentes antes de crear contenido nuevo.
- Cada guía debe tener utilidad práctica, título específico, fecha de revisión, enlaces internos y una llamada a solicitar presupuesto.
- Comprobar legislación y vigencia de la información antes de publicar; no incluir datos de clientes ni expedientes.
- Mantener revisión humana antes de fusionar cualquier cambio editorial.
- Medir mensualmente clics, impresiones, CTR y posición; los contactos recibidos deben registrarse separadamente, porque Search Console no mide conversiones.

## Alcance actual

La extracción semanal y el informe funcionan **cuando se configuren credenciales válidas de Search Console**. Sin credenciales, el flujo genera un aviso y no inventa métricas. La creación automática de artículos con IA y la medición de conversiones **no están activadas**.
