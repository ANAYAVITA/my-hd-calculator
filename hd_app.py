import streamlit as st
import swisseph as swe
import datetime
import pytz
from geopy.geocoders import Nominatim

# Konfiguration der Swiss Ephemeris (Pfad zu den Dateien)
swe.set_ephe_path('') 

def get_hd_data(jd_ut, body_id):
    """Berechnet Tor und Linie für einen Himmelskörper."""
    res, ret = swe.calc_ut(jd_ut, body_id)
    longitude = res[0]
    # 360 Grad / 64 Tore = 5.625 Grad pro Tor
    gate = int(longitude / 5.625) + 1
    line = int((longitude % 5.625) / (5.625 / 6)) + 1
    return gate, line

st.title("Gabriebeles HD-Standort-Tool")

# Input-Bereich
with st.form("input_form"):
    date = st.date_input("Datum", datetime.date.today())
    time = st.time_input("Uhrzeit", datetime.time(12, 0))
    location_name = st.text_input("Ort (Stadt, Land)", "Berlin, Germany")
    submit = st.form_submit_button("Berechnen")

if submit:
    # 1. Geokodierung (Längen-/Breitengrad)
    geolocator = Nominatim(user_agent="hd_app")
    loc = geolocator.geocode(location_name)
    
    # 2. Zeit-Korrektur (Wichtig: Alles muss auf UTC normiert werden)
    # Hinweis: In einer vollen Version müsste hier die Zeitzone des Ortes geladen werden.
    dt = datetime.combine(date, time)
    jd_ut = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)

    # 3. Berechnung der Positionen (Personality)
    bodies = {
        "Sonne": swe.SUN,
        "Mond": swe.MOON,
        "Chiron": 15,
        "Saturn": swe.SATURN
    }
    
    st.subheader("Aktuelle Planetenstände (Personality)")
    for name, bid in bodies.items():
        gate, line = get_hd_data(jd_ut, bid)
        st.write(f"**{name}:** Tor {gate}.{line}")

    # 4. Berechnung des Design-Zeitpunkts (88 Grad Sonnenbogen zurück)
    # Hier müsste eine iterative Suche implementiert werden.
