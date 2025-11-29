import streamlit as st
from datetime import date, datetime, timedelta

# -------------------- CONFIGURACIÓN --------------------
st.set_page_config(
    page_title="Citas Intravítreas y Contador de Semanas",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 Asistente de Citación para la Consulta de Mácula")

# ==========================================================
# FUNCIÓN DE RESETEO
# ==========================================================
def resetear():
    """Recarga la página para limpiar todos los campos."""
    st.session_state.clear()
    st.rerun()

# ==========================================================
# SECCIÓN 1: CONTADOR DE SEMANAS DESDE LA ÚLTIMA VISITA
# ==========================================================
st.header("📆 Contador de Semanas desde la Última Visita")

fecha_ultima = st.date_input(
    "Fecha de última visita",
    value=None,
    min_value=date(2000, 1, 1),
    max_value=date.today(),
    format="DD-MM-YYYY",
    key="fecha_ultima"
)

if fecha_ultima:
    hoy = date.today()
    diferencia_dias = (hoy - fecha_ultima).days
    semanas = diferencia_dias // 7
    dias_restantes = diferencia_dias % 7
    st.write(f"Han pasado **{semanas} semanas** y **{dias_restantes} días** desde la última visita.")

st.markdown("---")

# ==========================================================
# SECCIÓN 2: CÁLCULO DE CITAS INTRAVÍTREAS
# ==========================================================
st.header("💉 Calculadora de Citas Intravítreas")

farmacos = ["AVASTIN", "XIMLUCI", "VABYSMO", "EYLEA 2MG", "EYLEA 8MG", "OTRO"]

# Entrada de fecha base (por defecto, hoy)
fecha_input = st.date_input(
    "Fecha del último tratamiento",
    datetime.today(),
    format="DD-MM-YYYY",
    key="fecha_input"
)

# Selector de ojo
ojo = st.selectbox("Ojo a tratar", ["Elige", "Derecho", "Izquierdo", "Ambos"], key="ojo")

# --- Funciones auxiliares ---
def formatear_semana(fecha):
    lunes = fecha - timedelta(days=fecha.weekday())
    viernes = lunes + timedelta(days=4)
    return f"{lunes.strftime('%d-%m-%Y')} al {viernes.strftime('%d-%m-%Y')}"

def lunes_a_viernes(fecha):
    while fecha.weekday() > 4:  # 0=lunes, 6=domingo
        fecha += timedelta(days=1)
    return fecha

def calcular_fechas(base, intervalos):
    fechas = []
    acumulado = base
    for semanas in intervalos:
        acumulado += timedelta(weeks=semanas)
        fechas.append(lunes_a_viernes(acumulado))
    return fechas

resultado = ""

# --- Ojo Derecho ---
if ojo in ["Derecho", "Ambos"]:
    st.subheader("Ojo Derecho")
    farmaco_d = st.selectbox("Fármaco OD", farmacos, key='farm_d')
    dosis_d = st.number_input("Número de dosis OD", min_value=1, step=1, key='dosis_d')
    intervalos_d = []
    for i in range(dosis_d):
        sem = st.number_input(f"Intervalo {i+1} (semanas) OD", min_value=0, step=1, key=f"int_d_{i}")
        intervalos_d.append(sem)

    if intervalos_d:
        fechas = calcular_fechas(fecha_input, intervalos_d)
        resultado += f"\nOD ({farmaco_d}):\n"
        for i, f in enumerate(fechas):
            resultado += f"Dosis {i+1}: semana del {formatear_semana(f)}\n"

# --- Ojo Izquierdo ---
if ojo in ["Izquierdo", "Ambos"]:
    st.subheader("Ojo Izquierdo")
    farmaco_i = st.selectbox("Fármaco OI", farmacos, key='farm_i')
    dosis_i = st.number_input("Número de dosis OI", min_value=1, step=1, key='dosis_i')
    intervalos_i = []
    for i in range(dosis_i):
        sem = st.number_input(f"Intervalo {i+1} (semanas) OI", min_value=0, step=1, key=f"int_i_{i}")
        intervalos_i.append(sem)

    if intervalos_i:
        fechas = calcular_fechas(fecha_input, intervalos_i)
        resultado += f"\nOI ({farmaco_i}):\n"
        for i, f in enumerate(fechas):
            resultado += f"Dosis {i+1}: semana del {formatear_semana(f)}\n"

# ==========================================================
# BOTONES DE ACCIÓN
# ==========================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("Calcular"):
        st.text_area("Resultado", resultado, height=300)

with col2:
    if st.button("🔄 Resetear todos los campos"):
        resetear()

# -------------------- PIE DE PÁGINA --------------------
st.markdown("---")
st.caption("Aplicación para uso clínico interno – © 2025, Dr. Jesús Zarallo MD, PhD. Hospital Universitario del Henares")