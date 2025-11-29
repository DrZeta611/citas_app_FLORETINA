import streamlit as st
from datetime import date, datetime, timedelta

# -------------------- CONFIGURACIÓN --------------------
st.set_page_config(
    page_title="Citas Intravítreas - Hospital Henares",
    page_icon="🩺",
    layout="centered"
)

# -------------------- TRADUCCIONES --------------------
TEXTOS = {
    "es": {
        "title": "🩺 Asistente de Citación - Consulta de Mácula",
        "seccion1": "📆 Contador de Semanas desde la Última Visita",
        "ultima_visita": "Fecha de última visita",
        "seccion2": "💉 Calculadora de Citas Intravítreas",
        "fecha_inicio": "Fecha del último tratamiento",
        "ojo": "Ojo a tratar",
        "elige": "Elige", "derecho": "Derecho", "izquierdo": "Izquierdo", "ambos": "Ambos",
        "od": "👁️ Ojo Derecho", "oi": "👁️ Ojo Izquierdo",
        "farmaco": "Fármaco", "dosis": "Número de dosis", "int_sem": "Intervalo {i} (semanas)",
        "plan_generado": "📋 Plan de Tratamiento Generado",
        "descargar": "📥 Descargar Plan", "resetear": "🔄 Resetear todos los campos",
        "footer": "Aplicación para uso clínico interno – © 2025, Dr. Jesús Zarallo MD, PhD",
        "servicio_henares": "Hospital Universitario del Henares",
        "servicio_viamed": "Viamed Santa Elena",
        "aviso_largo": "⚠️ Ha elegido un valor por encima de 24 semanas. ¿Está seguro?",
        "aviso_corto": "⚠️ Ha elegido un valor inferior a 4 semanas. ¿Está seguro?"
    },
    "en": {
        "title": "🩺 Intravitreal Scheduling Assistant - Macula Clinic",
        "seccion1": "📆 Weeks Counter Since Last Visit",
        "ultima_visita": "Date of last visit",
        "seccion2": "💉 Intravitreal Appointment Calculator",
        "fecha_inicio": "Date of last treatment",
        "ojo": "Eye to treat",
        "elige": "Choose", "derecho": "Right", "izquierdo": "Left", "ambos": "Both",
        "od": "👁️ Right Eye", "oi": "👁️ Left Eye",
        "farmaco": "Drug", "dosis": "Number of doses", "int_sem": "Interval {i} (weeks)",
        "plan_generado": "📋 Generated Treatment Plan",
        "descargar": "📥 Download Plan", "resetear": "🔄 Reset All Fields",
        "footer": "Clinical use application – © 2025, Dr. Jesús Zarallo MD, PhD",
        "servicio_henares": "Hospital Universitario del Henares",
        "servicio_viamed": "Viamed Santa Elena",
        "aviso_largo": "⚠️ You have selected a value above 24 weeks. Are you sure?",
        "aviso_corto": "⚠️ You have selected a value below 4 weeks. Are you sure?"
    }
}

# -------------------- ESTADO INICIAL --------------------
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"
if "fecha_base" not in st.session_state:
    st.session_state.fecha_base = datetime.today().date()

idioma = st.session_state.idioma
t = TEXTOS[idioma]

# -------------------- BOTÓN IDIOMA --------------------
col_lang, _ = st.columns([1, 4])
with col_lang:
    if st.button("🇪🇸🇬🇧" if idioma == "es" else "🇬🇧🇪🇸", key="cambiar_idioma"):
        st.session_state.idioma = "en" if idioma == "es" else "es"
        st.rerun()

st.title(t["title"])

# -------------------- FUNCIÓN RESETEO --------------------
def resetear():
    """Recarga la página para limpiar todos los campos."""
    for key in list(st.session_state.keys()):
        if not key.startswith(("idioma", "fecha_base")):
            del st.session_state[key]
    st.rerun()

# -------------------- FÁRMACOS ORDENADOS + OTRO --------------------
FARMACOS = [
    "Aflibercept 2mg (Eylea 2mg)", "Aflibercept 8mg (Eylea 8mg)",
    "Bevacizumab (Avastin)", "Bevacizumab (Mvasi)",
    "Brolucizumab (Beovu)", "Brolucizumab (Vsiqq)",
    "Faricimab (Vabysmo)",
    "Ranibizumab (Lucentis)", "Ranibizumab (Ranivisio)", "Ranibizumab (Ximluci)",
    "Ziv-aflibercept (Zaltrap)",
    "Otro"
]

# ==========================================================
# SECCIÓN 1: CONTADOR DE SEMANAS DESDE LA ÚLTIMA VISITA
# ==========================================================
st.header(t["seccion1"])

fecha_ultima = st.date_input(
    t["ultima_visita"],
    value=None,
    min_value=date(2000, 1, 1),
    max_value=date.today(),
    format="DD/MM/YYYY",
    key="fecha_ultima"
)

if fecha_ultima:
    hoy = date.today()
    diferencia_dias = (hoy - fecha_ultima).days
    semanas = diferencia_dias // 7
    dias_restantes = diferencia_dias % 7
    semanas_text = f"**{semanas} weeks and {dias_restantes} days**" if idioma == "en" else f"**{semanas} semanas y {dias_restantes} días**"
    st.success(semanas_text, icon="✅")

st.markdown("---")

# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================
def formatear_semana(fecha):
    lunes = fecha - timedelta(days=fecha.weekday())
    viernes = lunes + timedelta(days=4)
    return f"{lunes.strftime('%d-%m-%Y')} al {viernes.strftime('%d-%m-%Y')}"

def lunes_a_viernes(fecha):
    while fecha.weekday() > 4:
        fecha += timedelta(days=1)
    return fecha

def calcular_fechas(base, intervalos):
    fechas = []
    acumulado = base
    for semanas in intervalos:
        if semanas > 0:
            acumulado += timedelta(weeks=semanas)
            fechas.append(lunes_a_viernes(acumulado))
    return fechas

def mostrar_aviso_intervalo(valor):
    """Muestra aviso si intervalo está fuera de rango recomendado"""
    if valor >= 24:
        st.warning(t["aviso_largo"], icon="⚠️")
    elif valor < 4 and valor > 0:
        st.warning(t["aviso_corto"], icon="⚠️")

# ==========================================================
# SECCIÓN 2: CÁLCULO DE CITAS INTRAVÍTREAS
# ==========================================================
st.header(t["seccion2"])

# Entrada de fecha base
fecha_base = st.date_input(
    t["fecha_inicio"],
    value=st.session_state.fecha_base,
    format="DD/MM/YYYY",
    key="fecha_base"
)

# Selector de ojo
ojo = st.selectbox(t["ojo"], [t["elige"], t["derecho"], t["izquierdo"], t["ambos"]], key="ojo")

resultado = ""

# --- Ojo Derecho ---
if ojo in [t["derecho"], t["ambos"]]:
    st.subheader(t["od"])
    farmaco_d = st.selectbox(t["farmaco"] + " OD", FARMACOS, key='farm_d')
    dosis_d = st.number_input(t["dosis"] + " OD", min_value=0, max_value=12, value=0, step=1, key='dosis_d')
    
    intervalos_d = []
    if dosis_d > 0:
        for i in range(dosis_d):
            label = t["int_sem"].format(i=i+1)
            sem = st.number_input(label + " OD", min_value=0, max_value=30, value=0, step=1, key=f"int_d_{i}")
            intervalos_d.append(sem)
            mostrar_aviso_intervalo(sem)

    if intervalos_d and any(sem > 0 for sem in intervalos_d):
        fechas = calcular_fechas(fecha_base, intervalos_d)
        resultado += f"\n**OD ({farmaco_d})**:\n"
        for i, f in enumerate(fechas):
            semana_str = formatear_semana(f)
            resultado += f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({semana_str})\n"

# --- Ojo Izquierdo ---
if ojo in [t["izquierdo"], t["ambos"]]:
    st.subheader(t["oi"])
    farmaco_i = st.selectbox(t["farmaco"] + " OI", FARMACOS, key='farm_i')
    dosis_i = st.number_input(t["dosis"] + " OI", min_value=0, max_value=12, value=0, step=1, key='dosis_i')
    
    intervalos_i = []
    if dosis_i > 0:
        for i in range(dosis_i):
            label = t["int_sem"].format(i=i+1)
            sem = st.number_input(label + " OI", min_value=0, max_value=30, value=0, step=1, key=f"int_i_{i}")
            intervalos_i.append(sem)
            mostrar_aviso_intervalo(sem)

    if intervalos_i and any(sem > 0 for sem in intervalos_i):
        fechas = calcular_fechas(fecha_base, intervalos_i)
        if resultado:
            resultado += "\n"
        resultado += f"**OI ({farmaco_i})**:\n"
        for i, f in enumerate(fechas):
            semana_str = formatear_semana(f)
            resultado += f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({semana_str})\n"

# ==========================================================
# BOTONES DE ACCIÓN
# ==========================================================
if resultado:
    st.markdown("### " + t["plan_generado"])
    st.code(resultado, language="text")
    st.download_button(t["descargar"], resultado, "plan_citas.txt", use_container_width=True)

col1, col2 = st.columns([3, 1])
with col1:
    if st.button(t["resetear"], use_container_width=True):
        resetear()

# -------------------- PIE DE PÁGINA CON ENLACES LIMPIOS --------------------
st.markdown("---")
st.caption(t["footer"])

# Enlaces limpios con iconos distintos
col_henares, col_viamed = st.columns(2)
with col_henares:
    st.markdown(f"🏥 **[{t['servicio_henares']}](https://www.comunidad.madrid/hospital/henares/profesionales/servicios-quirurgicos/oftalmologia)**")
with col_viamed:
    st.markdown(f"🏢 **[{t['servicio_viamed']}](https://www.viamedsalud.com/hospital-santa-elena/encuentra-tu-medico/?Nombre=zarallo&Especialidad=)**")
