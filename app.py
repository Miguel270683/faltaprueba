import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

def procesar_tareo(df):
    """Función para procesar el tareo y calcular faltas"""
    try:
        # Crear tabla dinámica para consolidar horas por día
        tareo_pivot = df.pivot_table(
            index=["DNI", "Apellidos y Nombres"],
            columns="DIA",
            values="HORAS TRABAJ.",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        # Ordenar los días de la semana
        dias_orden = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        columnas = ["DNI", "Apellidos y Nombres"] + dias_orden

        # Agregar columnas que falten si algún día no apareció en el dataset
        for dia in dias_orden:
            if dia not in tareo_pivot.columns:
                tareo_pivot[dia] = 0

        # Calcular el total de horas semanales por trabajador
        tareo_pivot["Total Semanal"] = tareo_pivot[dias_orden].sum(axis=1)

        # Reordenar las columnas
        tareo_final = tareo_pivot[columnas + ["Total Semanal"]].copy()

        # Reemplazar 0 por 'F' en los días de lunes a sábado
        for dia in ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]:
            if dia in tareo_final.columns:
                tareo_final[dia] = tareo_final[dia].apply(lambda x: "F" if x == 0 else x)

        # Calcular el total de faltas por trabajador
        tareo_final["Total Faltas"] = tareo_final[dias_orden].apply(
            lambda row: sum(str(x).strip().upper() == "F" for x in row), axis=1
        )

        # Reordenar columnas finales
        columnas_finales = ["DNI", "Apellidos y Nombres"] + dias_orden + ["Total Semanal", "Total Faltas"]
        tareo_final = tareo_final[columnas_finales]

        return tareo_final

    except Exception as e:
        st.error(f"Error al procesar el tareo: {str(e)}")
        return None

def generar_reporte_tramos_faltas(tareo_final, fecha_inicio_semana):
    """Función para generar el segundo reporte de tramos de faltas con fechas"""
    try:
        # Días de la semana y su offset
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        offset_dias = {dia: fecha_inicio_semana + timedelta(days=i) for i, dia in enumerate(dias_semana)}

        # Lista para guardar tramos detectados
        tramos_faltas = []

        # Analizar por trabajador
        for _, fila in tareo_final.iterrows():
            dni = fila["DNI"]
            nombres = fila["Apellidos y Nombres"]
            tramo = []

            for dia in dias_semana:
                valor = str(fila.get(dia, "")).strip().upper()
                if valor == "F":
                    tramo.append(dia)
                else:
                    if tramo:
                        tramos_faltas.append({
                            "DNI": dni,
                            "Apellidos y Nombres": nombres,
                            "Fecha Inicial": offset_dias[tramo[0]].strftime("%d/%m/%Y"),
                            "Cantidad de Días": len(tramo),
                            "Fecha Final": offset_dias[tramo[-1]].strftime("%d/%m/%Y")
                        })
                        tramo = []

            # Si termina la semana con faltas
            if tramo:
                tramos_faltas.append({
                    "DNI": dni,
                    "Apellidos y Nombres": nombres,
                    "Fecha Inicial": offset_dias[tramo[0]].strftime("%d/%m/%Y"),
                    "Cantidad de Días": len(tramo),
                    "Fecha Final": offset_dias[tramo[-1]].strftime("%d/%m/%Y")
                })

        # Convertir resultado a DataFrame
        df_tramos = pd.DataFrame(tramos_faltas)
        
        return df_tramos

    except Exception as e:
        st.error(f"Error al generar reporte de tramos: {str(e)}")
        return None

def main():
    st.title("📊 Control de Asistencia y Faltas")
    st.markdown("### Procesa archivos Excel para generar reportes de asistencia semanal")
    
    # Configuración de fecha de inicio de semana
    st.sidebar.header("⚙️ Configuración")
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio de semana (Lunes)",
        value=datetime.now().date() - timedelta(days=datetime.now().weekday()),
        help="Selecciona el lunes de la semana que quieres analizar"
    )
    
    # Información sobre el formato esperado
    with st.expander("ℹ️ Formato de archivo esperado"):
        st.markdown("""
        **El archivo Excel debe contener las siguientes columnas:**
        - `DNI`: Documento de identidad del trabajador
        - `Apellidos y Nombres`: Nombre completo del trabajador
        - `DIA`: Día de la semana (lunes, martes, miércoles, jueves, viernes, sábado, domingo)
        - `HORAS TRABAJ.`: Horas trabajadas en el día (número o 0 para ausencia)
        
        **Procesamiento realizado:**
        - Consolida horas trabajadas por día para cada empleado
        - Marca con "F" los días sin horas trabajadas (faltas)
        - Calcula total de horas semanales por empleado
        - Cuenta el total de faltas por empleado
        - Genera reporte consolidado por semana
        """)
    
    # Upload file
    uploaded_file = st.file_uploader(
        "📁 Selecciona el archivo Excel con datos de asistencia",
        type=['xlsx', 'xls'],
        help="Sube un archivo Excel con los datos de asistencia"
    )
    
    if uploaded_file is not None:
        try:
            # Read the Excel file
            with st.spinner("📖 Leyendo archivo Excel..."):
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Archivo cargado exitosamente. {len(df)} registros encontrados.")
            
            # Verificar columnas requeridas
            columnas_requeridas = ["DNI", "Apellidos y Nombres", "DIA", "HORAS TRABAJ."]
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"❌ Faltan las siguientes columnas: {', '.join(columnas_faltantes)}")
                st.info("Asegúrate de que el archivo tenga todas las columnas requeridas.")
                return
            
            # Display original data
            st.subheader("📋 Datos originales")
            st.dataframe(df, use_container_width=True)
            
            # Mostrar información básica
            col1, col2, col3 = st.columns(3)
            with col1:
                total_empleados = df["DNI"].nunique()
                st.metric("Total Empleados", total_empleados)
            with col2:
                total_registros = len(df)
                st.metric("Total Registros", total_registros)
            with col3:
                dias_unicos = df["DIA"].nunique()
                st.metric("Días Únicos", dias_unicos)
            
            # Process data
            if st.button("🔄 Procesar control de asistencia", type="primary"):
                with st.spinner("⚙️ Procesando datos de asistencia..."):
                    tareo_final = procesar_tareo(df)
                    
                    if tareo_final is not None:
                        st.success("✅ Datos procesados exitosamente!")
                        
                        # Display processed data
                        st.subheader("📊 Reporte 1: Asistencia Semanal Consolidada")
                        st.dataframe(tareo_final, use_container_width=True)
                        
                        # Summary statistics
                        st.subheader("📈 Resumen de Asistencia")
                        
                        # Estadísticas por empleado
                        empleados_con_faltas = len(tareo_final[tareo_final["Total Faltas"] > 0])
                        empleados_sin_faltas = len(tareo_final[tareo_final["Total Faltas"] == 0])
                        promedio_horas = tareo_final["Total Semanal"].mean()
                        total_faltas_general = tareo_final["Total Faltas"].sum()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Empleados con Faltas", empleados_con_faltas)
                        
                        with col2:
                            st.metric("Empleados sin Faltas", empleados_sin_faltas)
                        
                        with col3:
                            st.metric("Promedio Horas/Semana", f"{promedio_horas:.1f}")
                        
                        with col4:
                            st.metric("Total Faltas General", total_faltas_general)
                        
                        # Empleados con más faltas
                        if empleados_con_faltas > 0:
                            st.subheader("⚠️ Empleados con Mayor Número de Faltas")
                            top_faltas = tareo_final[tareo_final["Total Faltas"] > 0].nlargest(5, "Total Faltas")[
                                ["Apellidos y Nombres", "DNI", "Total Faltas", "Total Semanal"]
                            ]
                            st.dataframe(top_faltas, use_container_width=True)
                        
                        # Análisis por día
                        st.subheader("📅 Análisis de Faltas por Día")
                        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
                        faltas_por_dia = {}
                        
                        for dia in dias_semana:
                            if dia in tareo_final.columns:
                                faltas_dia = sum(tareo_final[dia].astype(str).str.upper() == "F")
                                faltas_por_dia[dia.capitalize()] = faltas_dia
                        
                        if faltas_por_dia:
                            col1, col2 = st.columns(2)
                            with col1:
                                for i, (dia, faltas) in enumerate(list(faltas_por_dia.items())[:3]):
                                    st.metric(f"Faltas {dia}", faltas)
                            with col2:
                                for i, (dia, faltas) in enumerate(list(faltas_por_dia.items())[3:]):
                                    st.metric(f"Faltas {dia}", faltas)
                        
                        # Generar segundo reporte - Tramos de faltas
                        st.subheader("📊 Reporte 2: Tramos de Faltas con Fechas")
                        
                        fecha_inicio_datetime = datetime.combine(fecha_inicio, datetime.min.time())
                        df_tramos = generar_reporte_tramos_faltas(tareo_final, fecha_inicio_datetime)
                        
                        if df_tramos is not None and not df_tramos.empty:
                            st.dataframe(df_tramos, use_container_width=True)
                            
                            # Estadísticas del segundo reporte
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                total_tramos = len(df_tramos)
                                st.metric("Total Tramos de Faltas", total_tramos)
                            with col2:
                                if not df_tramos.empty:
                                    promedio_dias = df_tramos["Cantidad de Días"].mean()
                                    st.metric("Promedio Días por Tramo", f"{promedio_dias:.1f}")
                            with col3:
                                if not df_tramos.empty:
                                    max_dias = df_tramos["Cantidad de Días"].max()
                                    st.metric("Máximo Días Consecutivos", max_dias)
                        else:
                            st.info("✅ ¡Excelente! No se encontraron tramos de faltas consecutivas en esta semana.")
                        
                        # Download processed files
                        st.subheader("💾 Descargar Reportes")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Reporte 1: Tareo semanal
                            output1 = io.BytesIO()
                            tareo_final.to_excel(output1, sheet_name='Tareo_Semanal', index=False, engine='openpyxl')
                            excel_data1 = output1.getvalue()
                            
                            st.download_button(
                                label="📥 Reporte 1: Asistencia Semanal",
                                data=excel_data1,
                                file_name="tareo_semanal_consolidado.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                help="Descarga el reporte consolidado de asistencia semanal"
                            )
                        
                        with col2:
                            # Reporte 2: Tramos de faltas
                            if df_tramos is not None and not df_tramos.empty:
                                output2 = io.BytesIO()
                                df_tramos.to_excel(output2, sheet_name='Tramos_Faltas', index=False, engine='openpyxl')
                                excel_data2 = output2.getvalue()
                                
                                st.download_button(
                                    label="📥 Reporte 2: Tramos de Faltas",
                                    data=excel_data2,
                                    file_name="reporte_faltas_semanales_fechas.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    help="Descarga el reporte de tramos de faltas con fechas"
                                )
                            else:
                                st.info("No hay tramos de faltas para descargar")
        
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {str(e)}")
            st.error("Asegúrate de que el archivo tenga el formato correcto y las columnas requeridas.")
    
    else:
        st.info("👆 Por favor, sube un archivo Excel para comenzar el procesamiento.")
    
    # Footer
    st.markdown("---")
    st.markdown("📍 **Nota**: Este sistema consolida automáticamente la asistencia semanal y identifica faltas de los empleados.")

if __name__ == "__main__":
    main()