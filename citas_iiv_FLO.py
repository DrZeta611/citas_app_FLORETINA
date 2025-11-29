import streamlit as st
from datetime import date, datetime, timedelta

# Configuración
st.set_page_config(page_title="Intravitreal Scheduler", page_icon="🩺", layout="centered")

# Traducciones
TEXTOS = {
    "es": {
        "title": "🩺 Asistente de Citación - Mácula",
        "seccion1": "📆 Semanas desde Última Visita",
        "ultima_visita": "Última visita",
        "seccion2": "💉 Plan de Tratamiento",
        "fecha_inicio": "Fecha inicio",
        "ojo": "Ojo",
        "elige": "Elige", "derecho": "Derecho", "izquierdo": "Izquierdo", "ambos": "Ambos",
        "od": "👁️ OD", "oi": "👁️ OI", "farmaco": "Fármaco", "dosis": "Dosis",
        "int_sem": "Int.{i+1} (sem)", "plan_generado": "📋 Plan Generado",
        "descargar": "📥 Descargar Plan", "resetear": "🔄 Resetear",
        "footer": "© 2025 Dr. Jesús Zarallo MD, PhD - Hospital Universitario del Henares",
        "servicio": "Servicio de Oftalmología Hospital Henares"
    },
    "en": {
        "title": "🩺 Intravitreal Scheduling Assistant - Macula",
        "seccion1": "📆 Weeks Since Last Visit",
        "ultima_visita": "Last visit",
        "seccion2": "💉 Treatment Plan",
        "fecha_inicio": "Start date",
        "ojo": "Eye", "elige": "Choose", "derecho": "Right", "izquierdo": "Left", "ambos": "Both",
        "od": "👁️ OD", "oi": "👁️ OI", "farmaco": "Drug", "dosis": "Doses",
        "int_sem": "Int.{i+1} (wks)", "plan_generado": "📋 Generated Plan",
        "descargar": "📥 Download Plan", "resetear": "🔄 Reset",
        "footer": "© 2025 Dr. Jesús Zarallo MD, PhD - Hospital Universitario del Henares",
        "servicio": "Ophthalmology Service Hospital Henares"
    }
}

# Estado inicial
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"
if "fecha_base" not in st.session_state:
    st.session_state.fecha_base = datetime.today().date()

idioma = st.session_state.idioma
t = TEXTOS[idioma]

# Botón idioma
col_lang, _ = st.columns([1,4])
with col_lang:
    if st.button("🇪🇸🇬🇧" if idioma == "es" else "🇪🇸🇬🇧", key="cambiar_idioma"):
        st.session_state.idioma = "en" if idioma == "es" else "es"
        st.rerun()

st.title(t["title"])

def resetear():
    for key in list(st.session_state.keys()):
        if not key.startswith("idioma"):
            del st.session_state[key]
    st.rerun()

# FÁRMACOS con principio activo
FARMACOS = [
    "Bevacizumab (Avastin)", "Aflibercept 8mg (Eylea 8mg)", "Bevacizumab (Mvasi)",
    "Brolucizumab (Beovu)", "Faricimab (Vabysmo)", "Ranibizumab (Lucentis)",
    "Brolucizumab (Vsiqq)", "Ranibizumab (Ranivisio)", "Ziv-aflibercept (Zaltrap)",
    "Ranibizumab (Ximluci)"
]

# SECCIÓN 1: Contador semanas
st.header(t["seccion1"])
fecha_ultima = st.date_input(t["ultima_visita"], value=None, format="DD/MM/YYYY", key="fecha_ultima")
if fecha_ultima:
    diff = (date.today() - fecha_ultima).days
    semanas_text = f"**{diff//7} weeks and {diff%7} days**" if idioma=="en" else f"**{diff//7} semanas y {diff%7} días**"
    st.success(semanas_text, icon="✅")

st.divider()

# FUNCIONES AUXILIARES
def formatear_semana(fecha):
    lunes = fecha - timedelta(days=fecha.weekday())
    viernes = lunes + timedelta(days=4)
    return f"{lunes.strftime('%d-%m-%Y')} al {viernes.strftime('%d-%m-%Y')}"

def lunes_a_viernes(fecha):
    while fecha.weekday() > 4:
        fecha += timedelta(days=1)
    return fecha

def calcular_fechas(fecha_base, intervalos):
    fechas = []
    acumulado = fecha_base
    for semanas in intervalos:
        if semanas > 0:
            acumulado += timedelta(weeks=semanas)
            fecha_ajustada = lunes_a_viernes(acumulado)
            fechas.append(fecha_ajustada)
    return fechas

# SECCIÓN 2: Calculadora
st.header(t["seccion2"])
fecha_base = st.date_input(t["fecha_inicio"], value=st.session_state.fecha_base, format="DD/MM/YYYY", key="fecha_base")
ojo = st.selectbox(t["ojo"], [t["elige"], t["derecho"], t["izquierdo"], t["ambos"]], key="ojo")

resultado = ""
if ojo != t["elige"]:
    col_od, col_oi = st.columns(2)
    
   # SECCIÓN 2: Calculadora (CORREGIDA)
st.header(t["seccion2"])
fecha_base = st.date_input(t["fecha_inicio"], value=st.session_state.fecha_base, format="DD/MM/YYYY", key="fecha_base")
ojo = st.selectbox(t["ojo"], [t["elige"], t["derecho"], t["izquierdo"], t["ambos"]], key="ojo")

resultado = ""
if ojo != t["elige"]:
    col_od, col_oi = st.columns(2)
    
    with col_od:
        st.subheader(t["od"])
        if ojo in [t["derecho"], t["ambos"]]:
            farmaco_od = st.selectbox(t["farmaco"], FARMACOS, key="f_od")
            dosis_od = st.number_input(t["dosis"], 1, 12, 3, key="d_od")
            
            # ✅ CORREGIDO: bucle explícito para labels dinámicos
            intervalos_od = []
            for i in range(dosis_od):
                label = t["int_sem"].format(i=i)
                sem = st.number_input(label, 0, 20, 4+i, key=f"int_od_{i}")
                intervalos_od.append(sem)
            
            fechas_od = calcular_fechas(fecha_base, intervalos_od)
            if fechas_od:
                resultado += f"**OD ({farmaco_od})**:\n"
                for i, f in enumerate(fechas_od):
                    semana_str = formatear_semana(f)
                    resultado += f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({semana_str})\n"
    
    with col_oi:
        st.subheader(t["oi"])
        if ojo in [t["izquierdo"], t["ambos"]]:
            farmaco_oi = st.selectbox(t["farmaco"], FARMACOS, key="f_oi")
            dosis_oi = st.number_input(t["dosis"], 1, 12, 3, key="d_oi")
            
            # ✅ CORREGIDO: mismo fix para OI
            intervalos_oi = []
            for i in range(dosis_oi):
                label = t["int_sem"].format(i=i)
                sem = st.number_input(label, 0, 20, 4+i, key=f"int_oi_{i}")
                intervalos_oi.append(sem)
            
            fechas_oi = calcular_fechas(fecha_base, intervalos_oi)
            if fechas_oi:
                resultado += f"\n**OI ({farmaco_oi})**:\n"
                for i, f in enumerate(fechas_oi):
                    semana_str = formatear_semana(f)
                    resultado += f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({semana_str})\n"

    st.code(resultado, language="text")
    st.download_button(t["descargar"], resultado, "plan_citas.txt")

# BOTONES
col1, col2 = st.columns([3,1])
with col1:
    if st.button(t["resetear"], use_container_width=True):
        resetear()

# PIE DE PÁGINA CON ENLACE
st.markdown("---")
st.caption(t["footer"])
st.markdown(f"🔗 **[ {t['servicio']} ](https://www.comunidad.madrid/hospital/henares/profesionales/servicios-quirurgicos/oftalmologia)**")
