# Control de Asistencia y Faltas

Una aplicación web desarrollada con Streamlit para procesar datos de asistencia laboral desde archivos Excel, generando reportes consolidados de faltas y horas trabajadas por empleado.

## Características

- **Carga de archivos Excel**: Procesa archivos con datos de asistencia diaria
- **Configuración de fechas**: Selecciona la fecha de inicio de semana para análisis preciso
- **Consolidación automática**:
  - Agrupa horas trabajadas por empleado y día de la semana
  - Marca automáticamente faltas (F) en días sin horas registradas
  - Calcula totales semanales por empleado
  - Cuenta faltas totales por empleado
- **Doble sistema de reportes**:
  - **Reporte 1**: Asistencia semanal consolidada por empleado
  - **Reporte 2**: Tramos de faltas consecutivas con fechas reales
- **Análisis detallado**:
  - Empleados con mayor número de faltas
  - Estadísticas de faltas por día de la semana
  - Métricas de tramos de faltas consecutivas
  - Identificación de patrones de ausentismo
- **Interfaz intuitiva**: Aplicación web fácil de usar
- **Exportación dual**: Descarga ambos reportes en archivos Excel separados

## Formato de archivo requerido

El archivo Excel debe contener las siguientes columnas:

- `DNI`: Documento de identidad del trabajador
- `Apellidos y Nombres`: Nombre completo del trabajador
- `DIA`: Día de la semana (lunes, martes, miércoles, jueves, viernes, sábado, domingo)
- `HORAS TRABAJ.`: Horas trabajadas en el día (número o 0 para ausencia)

## Procesamiento realizado

1. **Consolidación**: Agrupa datos por empleado y día de la semana
2. **Marcado de faltas**: Convierte horas 0 en "F" (falta) para días laborales
3. **Reporte 1 - Asistencia semanal**:
   - Total de horas semanales por empleado
   - Total de faltas por empleado
   - Estadísticas generales de asistencia
4. **Reporte 2 - Tramos de faltas**:
   - Identifica faltas consecutivas por empleado
   - Calcula fechas reales de inicio y fin de cada tramo
   - Cuenta días consecutivos de ausencia
5. **Análisis**: Patrones de ausentismo y empleados con mayor número de faltas

## Instalación local

1. Clona este repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

## Despliegue en Streamlit Cloud

1. Haz fork de este repositorio
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio de GitHub
4. Selecciona `app.py` como archivo principal
5. Haz clic en "Deploy"

## Estructura del proyecto

```
├── app.py                    # Aplicación principal de Streamlit
├── .streamlit/
│   └── config.toml          # Configuración de Streamlit
├── requirements.txt         # Dependencias Python
└── README.md               # Este archivo
```

## Reportes generados

### Reporte 1: Tareo Semanal Consolidado
- Empleados organizados por DNI y nombre
- Horas trabajadas por día de la semana
- Faltas marcadas como "F"
- Total semanal de horas por empleado
- Total de faltas por empleado

### Reporte 2: Tramos de Faltas con Fechas
- DNI y nombre del empleado
- Fecha inicial del tramo de faltas
- Cantidad de días consecutivos
- Fecha final del tramo de faltas
- Solo incluye tramos de faltas consecutivas

## Tecnologías utilizadas

- **Streamlit**: Framework web para aplicaciones de datos
- **Pandas**: Procesamiento de datos y archivos Excel
- **OpenPyXL**: Lectura y escritura de archivos Excel
- **Python**: Análisis de datos y lógica de negocio