# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import date, datetime

# --- Sigurnosni fallback za COUNTRIES ---
try:
    COUNTRIES  # noqa
except NameError:
    try:
        import pycountry
        COUNTRIES = {c.name: getattr(c, "alpha_3", "") for c in pycountry.countries}
    except Exception:
        COUNTRIES = {
            "Hrvatska":"CRO","Srbija":"SRB","Slovenija":"SVN","Bosna i Hercegovina":"BIH",
            "Mađarska":"HUN","Italija":"ITA","Njemačka":"DEU","Austrija":"AUT",
            "Francuska":"FRA","Španjolska":"ESP","Švicarska":"CHE","Turska":"TUR",
            "SAD":"USA","Kanada":"CAN","UK":"GBR"
        }

def get_conn():
    return sqlite3.connect("club.db")

def save_upload(file, folder):
    import os
    import pathlib
    if not file:
        return ""
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    path = os.path.join(folder, file.name)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return path

def page_header(title, subtitle=""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)

def section_competitions():
    conn = get_conn()
    page_header("Natjecanja i rezultati", "Unos natjecanja, datoteka, rezultata i pretraga")

    KINDS = [
        "PRVENSTVO HRVATSKE","MEĐUNARODNI TURNIR","REPREZENTATIVNI NASTUP",
        "HRVAČKA LIGA ZA SENIORE","MEĐUNARODNA HRVAČKA LIGA ZA KADETE",
        "REGIONALNO PRVENSTVO","LIGA ZA DJEVOJČICE","OSTALO"
    ]
    REP_SUB = ["PRVENSTVO EUROPE","PRVENSTVO SVIJETA","PRVENSTVO BALKANA","UWW TURNIR"]
    STYLES = ["GR","FS","WW","BW","MODIFICIRANO"]
    AGES = ["POČETNICI","U11","U13","U15","U17","U20","U23","SENIORI"]

    with st.form("comp_form", clear_on_submit=False):
        kind = st.selectbox("Vrsta natjecanja", KINDS)
        rep_sub = st.selectbox("Podvrsta", REP_SUB) if kind=="REPREZENTATIVNI NASTUP" else ""
        name = st.text_input("Ime natjecanja")
        date_from = st.date_input("Datum od", value=date.today())
        date_to = st.date_input("Datum do", value=date.today())
        place = st.text_input("Mjesto")
        country = st.selectbox("Država", sorted(list(COUNTRIES.keys())))
        country_code = COUNTRIES.get(country,"")
        st.text_input("Kratica države", value=country_code, disabled=True)
        style = st.selectbox("Hrvački stil", STYLES)
        age_group = st.selectbox("Uzrast", AGES)
        team_rank = st.text_input("Ekipni poredak")
        submit = st.form_submit_button("Spremi")
    if submit:
        conn.execute("CREATE TABLE IF NOT EXISTS competitions(id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO competitions (name) VALUES (?)", (name,))
        conn.commit()
        st.success("Natjecanje spremljeno.")

st.set_page_config("HK Podravka Admin", layout="wide")
section_competitions()
