import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Citas Intravítreas", page_icon="🩺", layout="centered")

TEXTOS = {
    "es": {
        "title": "🩺 Asistente de Citación - Mácula",
        "seccion1": "📆 Semanas desde Última Visita", "ultima_visita": "Última visita",
        "seccion2": "💉 Plan de Tratamiento", "fecha_inicio": "Fecha inicio",
        "ojo": "Ojo", "elige": "Elige", "derecho": "Derecho", "izquierdo": "Izquierdo", "ambos": "Ambos",
        "od": "👁️ OD", "oi": "👁️ OI", "farmaco": "Fármaco", "dosis": "Dosis", "int_sem": "Int.{i} (sem)",
        "plan_generado": "📋 Plan Generado", "descargar": "📥 Descargar", "resetear": "🔄 Resetear",
        "footer": "© 2025 Dr. Jesús Zarallo MD, PhD", "henares": "🏥 H. Universitario Henares",
        "viamed": "🏢 Viamed Santa Elena",
        "aviso_largo": "⚠️ >24 sem. ¿Seguro?", "aviso_corto": "⚠️ <4 sem. ¿Seguro?"
    },
    "en": {
        "title": "🩺 Intravitreal Scheduler", "seccion1": "📆 Weeks Since Last Visit", "ultima_visita": "Last visit",
        "seccion2": "💉 Treatment Plan", "fecha_inicio": "Start date",
        "ojo": "Eye", "elige": "Choose", "derecho": "Right", "izquierdo": "Left", "ambos": "Both",
        "od": "👁️ OD", "oi": "👁️ OI", "farmaco": "Drug", "dosis": "Doses", "int_sem": "Int.{i} (wks)",
        "plan_generado": "📋 Generated Plan", "descargar": "📥 Download", "resetear": "🔄 Reset",
        "footer": "© 2025 Dr. Jesús Zarallo MD, PhD", "henares": "🏥 H. Universitario Henares",
        "viamed": "🏢 Viamed Santa Elena",
        "aviso_largo": "⚠️ >24 wks. Sure?", "aviso_corto": "⚠️ <4 wks. Sure?"
    }
}

# Estado
if "idioma" not in st.session_state: st.session_state.idioma = "es"
if "fecha_base" not in st.session_state: st.session_state.fecha_base = date.today()

idioma = st.session_state.idioma
t = TEXTOS[idioma]

# Idioma
if st.button("🇪🇸🇬🇧" if idioma == "es" else "🇬🇧🇪🇸"):
    st.session_state.idioma = "en" if idioma == "es" else "es"
    st.rerun()

st.title(t["title"])

def resetear(): 
    for k in list(st.session_state): 
        if not k.startswith("idioma"): del st.session_state[k]
    st.rerun()

FARMACOS = [
    "Aflibercept 2mg (Eylea 2mg)", "Aflibercept 8mg (Eylea 8mg)", "Bevacizumab (Avastin)", 
    "Bevacizumab (Mvasi)", "Brolucizumab (Beovu)", "Brolucizumab (Vsiqq)", "Faricimab (Vabysmo)",
    "Ranibizumab (Lucentis)", "Ranibizumab (Ranivisio)", "Ranibizumab (Ximluci)", "Ziv-aflibercept (Zaltrap)", "Otro"
]

# SECCIÓN 1
st.header(t["seccion1"])
if fecha_ultima := st.date_input(t["ultima_visita"], format="DD/MM/YYYY", key="fecha_ultima"):
    diff = (date.today() - fecha_ultima).days
    semanas_text = f"**{diff//7} semanas y {diff%7} días**" if idioma == "es" else f"**{diff//7} weeks and {diff%7} days**"
    st.success(semanas_text, icon="✅")

st.divider()

# FUNCIONES
def semana_laboral(fecha): 
    lunes = fecha - timedelta(days=fecha.weekday())
    return f"{lunes.strftime('%d-%m-%Y')} al {(lunes+timedelta(days=4)).strftime('%d-%m-%Y')}"

def ajustar_laboral(fecha): 
    while fecha.weekday() > 4: fecha += timedelta(days=1)
    return fecha

def calcular_fechas(base, ints): 
    return [ajustar_laboral(base + timedelta(weeks=w)) for w in ints if w > 0]

def aviso_intervalo(v): 
    if v >= 24: st.warning(t["aviso_largo"], icon="⚠️")
    elif 0 < v < 4: st.warning(t["aviso_corto"], icon="⚠️")

# SECCIÓN 2
st.header(t["seccion2"])
fecha_base = st.date_input(t["fecha_inicio"], st.session_state.fecha_base, format="DD/MM/YYYY", key="fecha_base")
ojo = st.selectbox(t["ojo"], [t["elige"], t["derecho"], t["izquierdo"], t["ambos"]], key="ojo")

resultado = ""
if ojo != t["elige"]:
    col_od, col_oi = st.columns(2)
    
    with col_od:
        if ojo in [t["derecho"], t["ambos"]]:
            st.subheader(t["od"])
            f_od = st.selectbox(t["farmaco"], FARMACOS, key="f_od")
            d_od = st.number_input(t["dosis"], 0, 12, 0, key="d_od")
            ints_od = [st.number_input(t["int_sem"].format(i=i+1), 0, 52, 0, key=f"i_od_{i}") 
                      for i in range(d_od)] if d_od else []
            for i in ints_od: aviso_intervalo(i)
            if any(i>0 for i in ints_od):
                fechas = calcular_fechas(fecha_base, ints_od)
                resultado += f"**OD ({f_od})**:\n" + "\n".join(f"D{i+1}: {f.strftime('%d-%m-%Y')} ({semana_laboral(f)})" 
                                                             for i,f in enumerate(fechas))
    
    with col_oi:
        if ojo in [t["izquierdo"], t["ambos"]]:
            st.subheader(t["oi"])
            f_oi = st.selectbox(t["farmaco"], FARMACOS, key="f_oi")
            d_oi = st.number_input(t["dosis"], 0, 12, 0, key="d_oi")
            ints_oi = [st.number_input(t["int_sem"].format(i=i+1), 0, 52, 0, key=f"i_oi_{i}") 
                      for i in range(d_oi)] if d_oi else []
            for i in ints_oi: aviso_intervalo(i)
            if any(i>0 for i in ints_oi) and resultado: resultado += "\n"
            if any(i>0 for i in ints_oi):
                fechas = calcular_fechas(fecha_base, ints_oi)
                resultado += f"**OI ({f_oi})**:\n" + "\n".join(f"D{i+1}: {f.strftime('%d-%m-%Y')} ({semana_laboral(f)})" 
                                                             for i,f in enumerate(fechas))

if resultado:
    st.markdown("### " + t["plan_generado"])
    st.code(resultado)
    st.download_button(t["descargar"], resultado, "plan.txt")

if st.button(t["resetear"]): resetear()

# PIE
st.markdown("---")
st.caption(t["footer"])
st.columns(2)[0].markdown(f"[{t['henares']}](https://www.comunidad.madrid/hospital/henares/profesionales/servicios-quirurgicos/oftalmologia)")
st.columns(2)[1].markdown(f"[{t['viamed']}](https://www.viamedsalud.com/hospital-santa-elena/encuentra-tu-medico/?Nombre=zarallo&Especialidad=)")
