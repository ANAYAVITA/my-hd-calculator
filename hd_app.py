import streamlit as st
import swisseph as swe
import datetime
from geopy.geocoders import Nominatim
import pandas as pd

# 1. System-Konfiguration: Daten direkt von der Quelle beziehen
# Dies verhindert Fehler, falls lokale Ephemeriden-Dateien fehlen
swe.set_ephe_path('') 

def get_hd_gate(longitude):
    """Berechnet Tor und Linie aus der ekliptikalen Länge."""
    # 360 Grad / 64 Tore = 5.625
    gate_float = longitude / 5.625
    gate = int(gate_float) + 1
    line = int((gate_float - int(gate_float)) * 6) + 1
    return f"{gate}.{line}"

def calculate_design_time(birth_jd):
    """Berechnet den Zeitpunkt 88 Grad Sonnenbogen vor der Geburt."""
    # Ermittle Sonnenstand zur Geburt
    res, ret = swe.calc_ut(birth_jd, swe.SUN)
    birth_sun_pos = res[0]
    
    # Ziel: Sonnenstand minus 88 Grad
    target_sun_pos = (birth_sun_pos - 88) % 360
    
    # Einfache Annäherung: 88 Grad entsprechen ca. 89.1 Tagen
    design_jd = birth_jd - 89.1
    return design_jd, target_sun_pos

st.set_page_config(page_title="HD Analyse-Tool", layout="wide")
st.title("Human Design Standortbestimmung")

# Eingabemaske
with st.sidebar:
    st.header("Geburtsdaten")
    d = st.date_input("Datum", datetime.date(1980, 1, 1))
    t = st.time_input("Uhrzeit", datetime.time(12, 0))
    # Wichtig: Für exakte Daten müsste hier noch die Zeitzone (UTC-Offset) rein
    utc_offset = st.number_input("Zeitzone (UTC Offset, z.B. 1 für Berlin)", value=1)

# Berechnung starten
jd_birth = swe.julday(d.year, d.month, d.day, (t.hour - utc_offset) + t.minute/60)
jd_design, target_sun = calculate_design_time(jd_birth)

# Definition der relevanten Körper (Invarianten des Systems)
bodies = {
    "Sonne": swe.SUN,
    "Mond": swe.MOON,
    "Chiron": 15,
    "Saturn": swe.SATURN,
    "Jupiter": swe.JUPITER,
    "Uranus": swe.URANUS,
    "Neptun": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Personality (Bewusst)")
    for name, id in bodies.items():
        res, ret = swe.calc_ut(jd_birth, id)
        st.write(f"**{name}:** {get_hd_gate(res[0])}")

with col2:
    st.subheader("Design (Unbewusst)")
    for name, id in bodies.items():
        res, ret = swe.calc_ut(jd_design, id)
        st.write(f"**{name}:** {get_hd_gate(res[0])}")

st.info("Hinweis: Dies ist eine strukturelle Berechnung auf Basis der Swiss Ephemeris. "
        "Die Design-Zeit wird hier über den Standard-Bogen von 88° genähert.")
