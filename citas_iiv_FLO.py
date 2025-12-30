import streamlit as st
from datetime import date, datetime, timedelta
from collections import defaultdict

st.set_page_config(page_title="Citas Intravítreas - Hospital Henares", page_icon="🩺", layout="centered")

TEXTOS = {
    "es": {
        "title": "🩺 Asistente de Citación - Consulta de Mácula",
        "seccion1": "📆 Contador de Semanas desde la Última Visita",
        "ultima_visita": "Fecha de última visita",
        "seccion2": "💉 Calculadora de Citas Intravítreas",
        "fecha_inicio": "Fecha del último tratamiento",
        "ojo": "Ojo a tratar", "elige": "Elige", "derecho": "Derecho", "izquierdo": "Izquierdo", "ambos": "Ambos",
        "od": "👁️ Ojo Derecho", "oi": "👁️ Ojo Izquierdo",
        "farmaco": "Fármaco", "dosis": "Número de dosis", "int_sem": "Intervalo {i} (semanas)",
        "plan_od": "📋 Plan OD", "plan_oi": "📋 Plan OI", "plan_total": "📅 Programación Cronológica",
        "plan_generado": "📋 Plan de Tratamiento Generado", "descargar": "📥 Descargar Plan", "resetear": "🔄 Resetear todos los campos",
        "footer": "Aplicación para uso clínico interno – © 2025, Dr. Jesús Zarallo MD, PhD",
        "servicio_henares": "Hospital Universitario del Henares",
        "servicio_viamed": "Viamed Santa Elena",
        "aviso_largo": "⚠️ Ha elegido un valor por encima de 24 semanas. ¿Está seguro?",
        "aviso_corto": "⚠️ Ha elegido un valor inferior a 4 semanas. ¿Está seguro?",
        "rango_semana": "al"
    },
    "en": {
        "title": "🩺 Intravitreal Scheduling Assistant - Macula Clinic",
        "seccion1": "📆 Weeks Counter Since Last Visit",
        "ultima_visita": "Date of last visit",
        "seccion2": "💉 Intravitreal Appointment Calculator",
        "fecha_inicio": "Date of last treatment",
        "ojo": "Eye to treat", "elige": "Choose", "derecho": "Right", "izquierdo": "Left", "ambos": "Both",
        "od": "👁️ OD", "oi": "👁️ OS",
        "farmaco": "Drug", "dosis": "Number of doses", "int_sem": "Interval {i} (weeks)",
        "farmaco_od": "Drug OD", "farmaco_oi": "Drug OS",
        "dosis_od": "Number of doses OD", "dosis_oi": "Number of doses OS",
        "plan_od": "📋 OD Plan", "plan_oi": "📋 OS Plan", "plan_total": "📅 Chronological Schedule",
        "plan_generado": "📋 Generated Treatment Plan", "descargar": "📥 Download Plan", "resetear": "🔄 Reset All Fields",
        "footer": "Clinical use application – © 2025, Dr. Jesús Zarallo MD, PhD",
        "servicio_henares": "Hospital Universitario del Henares",
        "servicio_viamed": "Viamed Santa Elena",
        "aviso_largo": "⚠️ You have selected a value above 24 weeks. Are you sure?",
        "aviso_corto": "⚠️ You have selected a value below 4 weeks. Are you sure?",
        "rango_semana": "to"
    }
}

# Estado inicial
if "idioma" not in st.session_state: 
    st.session_state.idioma = "es"
if "fecha_base" not in st.session_state: 
    st.session_state.fecha_base = date.today()

idioma = st.session_state.idioma
t = TEXTOS[idioma]

# Botón idioma
col_lang, _ = st.columns([1, 4])
with col_lang:
    if st.button("🇪🇸/🇬🇧" if idioma == "es" else "🇬🇧/🇪🇸", key="cambiar_idioma"):
        st.session_state.idioma = "en" if idioma == "es" else "es"
        st.rerun()

st.title(t["title"])

def resetear():
    claves_protegidas = {"idioma", "fecha_base"}
    for key in list(st.session_state.keys()):
        if key not in claves_protegidas:
            del st.session_state[key]
    st.rerun()

FARMACOS = [
    "Aflibercept 2mg (Eylea 2mg)", "Aflibercept 2mg (Afqlir)", "Aflibercept 8mg (Eylea 8mg)",
    "Bevacizumab (Avastin)", "Bevacizumab (Mvasi)",
    "Brolucizumab (Beovu)", "Brolucizumab (Vsiqq)",
    "Faricimab (Vabysmo)",
    "Ranibizumab (Lucentis)", "Ranibizumab (Ranivisio)", "Ranibizumab (Ximluci)",
    "Ziv-aflibercept (Zaltrap)", "Otro"
]

# SECCIÓN 1
st.header(t["seccion1"])
fecha_ultima = st.date_input(t["ultima_visita"], value=None, format="DD/MM/YYYY", key="fecha_ultima")
if fecha_ultima:
    diff = (date.today() - fecha_ultima).days
    semanas_text = f"**{diff//7} semanas y {diff%7} días**" if idioma == "es" else f"**{diff//7} weeks and {diff%7} days**"
    st.success(semanas_text, icon="✅")

st.divider()

# FUNCIONES AUXILIARES
def formatear_semana(fecha):
    lunes = fecha - timedelta(days=fecha.weekday())
    viernes = lunes + timedelta(days=4)
    return f"{lunes.strftime('%d-%m-%Y')} {t['rango_semana']} {viernes.strftime('%d-%m-%Y')}"

def ajustar_laboral(fecha):
    while fecha.weekday() > 4: 
        fecha += timedelta(days=1)
    return fecha

def calcular_fechas(base, intervalos):
    fechas = []
    acumulado = base
    for semanas in intervalos:
        if semanas > 0:
            acumulado += timedelta(weeks=semanas)
            fechas.append(ajustar_laboral(acumulado))
    return fechas

def mostrar_aviso_intervalo(valor):
    if valor >= 24: 
        st.warning(t["aviso_largo"], icon="⚠️")
    elif 0 < valor < 4: 
        st.warning(t["aviso_corto"], icon="⚠️")

def generar_programacion_cronologica(fechas_od, farmaco_od, fechas_oi, farmaco_oi):
    eventos_por_dia = defaultdict(list)
    for i, fecha in enumerate(fechas_od):
        eventos_por_dia[fecha].append(f"OD - {farmaco_od} (D{i+1})")
    for i, fecha in enumerate(fechas_oi):
        eventos_por_dia[fecha].append(f"OS - {farmaco_oi} (D{i+1})")
    fechas_ordenadas = sorted(eventos_por_dia.keys())
    return [(fecha, ", ".join(eventos_por_dia[fecha])) for fecha in fechas_ordenadas]

# SECCIÓN 2
st.header(t["seccion2"])
fecha_base = st.date_input(t["fecha_inicio"], value=st.session_state.fecha_base, format="DD/MM/YYYY", key="fecha_base")
ojo = st.selectbox(t["ojo"], [t["elige"], t["derecho"], t["izquierdo"], t["ambos"]], key="ojo")

# Variables de resultado
fechas_od = []
farmaco_od = ""
intervalos_od = []
dosis_od = 0
plan_od = []

fechas_oi = []
farmaco_oi = ""
intervalos_oi = []
dosis_oi = 0
plan_oi = []

if ojo != t["elige"]:
    col_od, col_oi = st.columns(2)
    
    # COLUMNA OD
    with col_od:
        if ojo in [t["derecho"], t["ambos"]]:
            st.subheader(t["od"])
            label_farmaco_od = t["farmaco_od"] if "farmaco_od" in t else t["farmaco"]
            label_dosis_od = t["dosis_od"] if "dosis_od" in t else t["dosis"]
            farmaco_od = st.selectbox(label_farmaco_od, FARMACOS, key="f_od")
            dosis_od = st.number_input(label_dosis_od, 0, 12, 0, key="d_od")
            
            intervalos_od = []
            if dosis_od > 0:
                for i in range(dosis_od):
                    base_label = t["int_sem"].format(i=i+1)
                    label = base_label + " OD" if idioma == "en" else base_label
                    sem = st.number_input(label, 0, 52, 0, key=f"int_od_{i}")
                    intervalos_od.append(sem)
                    mostrar_aviso_intervalo(sem)
            
            if intervalos_od and any(s > 0 for s in intervalos_od):
                fechas_od = calcular_fechas(fecha_base, intervalos_od)
                plan_od = [f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({formatear_semana(f)})" 
                          for i, f in enumerate(fechas_od)]
    
    # COLUMNA OI
    with col_oi:
        if ojo in [t["izquierdo"], t["ambos"]]:
            st.subheader(t["oi"])
            label_farmaco_oi = t["farmaco_oi"] if "farmaco_oi" in t else t["farmaco"]
            label_dosis_oi = t["dosis_oi"] if "dosis_oi" in t else t["dosis"]
            farmaco_oi = st.selectbox(label_farmaco_oi, FARMACOS, key="f_oi")
            dosis_oi = st.number_input(label_dosis_oi, 0, 12, 0, key="d_oi")
            
            intervalos_oi = []
            if dosis_oi > 0:
                for i in range(dosis_oi):
                    base_label = t["int_sem"].format(i=i+1)
                    label = base_label + " OS" if idioma == "en" else base_label
                    sem = st.number_input(label, 0, 52, 0, key=f"int_oi_{i}")
                    intervalos_oi.append(sem)
                    mostrar_aviso_intervalo(sem)
            
            if intervalos_oi and any(s > 0 for s in intervalos_oi):
                fechas_oi = calcular_fechas(fecha_base, intervalos_oi)
                plan_oi = [f"Dosis {i+1}: {f.strftime('%d-%m-%Y')} ({formatear_semana(f)})" 
                          for i, f in enumerate(fechas_oi)]

# PLANES ALINEADOS CON FÁRMACO EN TÍTULO
if plan_od or plan_oi:
    col_plan_od, col_plan_oi = st.columns(2)
    
    with col_plan_od:
        if plan_od:
            st.markdown(f"### {t['plan_od']} - **{farmaco_od}**")
            for linea in plan_od:
                st.write(f"**{linea}**")
        else:
            st.markdown("### " + t["plan_od"])
            st.info("📝 Configurar OD")
    
    with col_plan_oi:
        if plan_oi:
            st.markdown(f"### {t['plan_oi']} - **{farmaco_oi}**")
            for linea in plan_oi:
                st.write(f"**{linea}**")
        else:
            st.markdown("### " + t["plan_oi"])
            st.info("📝 Configurar OS")

# PROGRAMACIÓN CRONOLÓGICA TOTAL
if fechas_od or fechas_oi:
    st.markdown("---")
    st.markdown("### " + t["plan_total"])
    
    eventos = generar_programacion_cronologica(fechas_od, farmaco_od, fechas_oi, farmaco_oi)
    
    for fecha, tratamientos in eventos:
        st.write(f"**{fecha.strftime('%d-%m-%Y')}:** {tratamientos} ({formatear_semana(fecha)})")
    
    resultado_total = "PROGRAMACIÓN CRONOLÓGICA:\n\n" + "\n".join(
        f"{fecha.strftime('%d-%m-%Y')}: {tratamientos} ({formatear_semana(fecha)})" 
        for fecha, tratamientos in eventos
    )
    st.download_button(t["descargar"], resultado_total, "programacion_citas.txt", use_container_width=True)

col1, col2 = st.columns([3, 1])
with col1:
    if st.button(t["resetear"], use_container_width=True): 
        resetear()

# PIE DE PÁGINA
st.markdown("---")
st.caption(t["footer"])
col_henares, col_viamed = st.columns(2)
with col_henares:
    st.markdown(f"🏥 **[{t['servicio_henares']}](https://www.comunidad.madrid/hospital/henares/profesionales/servicios-quirurgicos/oftalmologia)**")
with col_viamed:
    st.markdown(f"🏢 **[{t['servicio_viamed']}](https://www.viamedsalud.com/hospital-santa-elena/encuentra-tu-medico/?Nombre=zarallo&Especialidad=)**")
