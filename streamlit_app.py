
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import date, datetime

# ---- Page config ----
st.set_page_config("HK Podravka Admin", layout="wide")

# ---- Countries (fallback-safe) ----
try:
    COUNTRIES  # noqa: F821
except NameError:
    try:
        import pycountry
        COUNTRIES = {c.name: c.alpha_2 for c in pycountry.countries}
    except Exception:
        # Minimal fallback if pycountry not available
        COUNTRIES = {
            "Hrvatska": "HR",
            "Slovenija": "SI",
            "Srbija": "RS",
            "Bosna i Hercegovina": "BA",
            "Mađarska": "HU",
            "Austrija": "AT",
            "Njemačka": "DE",
            "Italija": "IT",
        }

STYLES = ["GR", "FS", "WW"]  # grčko-rimski, slobodni, ženski
AGES = ["U9","U11","U13","U15","U17","U20","U23","Seniori","Veterani"]

# ---- DB helpers ----
def get_conn():
    return sqlite3.connect("club.db", check_same_thread=False)

def ensure_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            country_code TEXT,
            style TEXT,
            age_group TEXT,
            date_from TEXT,
            date_to TEXT,
            team_rank TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competition_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id INTEGER NOT NULL,
            athlete TEXT NOT NULL,
            weight_category TEXT,
            age_group TEXT,
            bouts_total INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            placement TEXT,
            metadata TEXT,
            FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE
        )
    """)
    conn.commit()

# ---- UI helpers ----
def iso_or_none(d):
    if not d:
        return None
    if isinstance(d, str):
        return d
    try:
        return d.isoformat()
    except Exception:
        return str(d)

# ---- Sections ----
def section_competitions():
    st.title("Natjecanja – administracija")
    conn = get_conn()
    ensure_tables(conn)

    tab1, tab2, tab3 = st.tabs(["📥 Novo natjecanje", "📝 Rezultati", "📊 Pregled"])

    with tab1:
        st.subheader("Dodaj natjecanje")
        with st.form("frm_comp"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Naziv *")
                city = st.text_input("Grad")
                country = st.selectbox("Država", sorted(COUNTRIES.keys()))
            with col2:
                country_code = COUNTRIES.get(country, "")
                st.text_input("Kratica države", value=country_code, disabled=True)
                style = st.selectbox("Hrvački stil", STYLES, index=0)
                age_group = st.selectbox("Uzrast", AGES, index=0)
            with col3:
                date_from = st.date_input("Datum od", value=date.today())
                date_to = st.date_input("Datum do", value=date.today())
                team_rank = st.text_input("Ekipni poredak")
            submit = st.form_submit_button("Spremi natjecanje")
        if submit:
            if not name:
                st.error("Naziv je obavezan.")
            else:
                conn.execute(
                    """INSERT INTO competitions
                    (name, city, country, country_code, style, age_group, date_from, date_to, team_rank)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (name, city, country, country_code, style, age_group, iso_or_none(date_from), iso_or_none(date_to), team_rank)
                )
                conn.commit()
                st.success("Natjecanje spremljeno.")

    with tab2:
        st.subheader("Dodaj rezultat")
        # fetch competitions for selection
        comps = pd.read_sql_query("SELECT id, name, date_from FROM competitions ORDER BY date_from DESC", conn)
        comp_map = {f"{r['name']} ({r['date_from']})": int(r['id']) for _, r in comps.iterrows()} if not comps.empty else {}
        with st.form("frm_res"):
            competition_label = st.selectbox("Natjecanje", list(comp_map.keys()) if comp_map else ["Nema natjecanja"])
            athlete = st.text_input("Natjecatelj *")
            col1, col2, col3 = st.columns(3)
            with col1:
                weight_category = st.text_input("Kategorija (npr. U15 57kg)")
            with col2:
                r_age_group = st.selectbox("Uzrast", AGES, index=0)
            with col3:
                placement = st.text_input("Plasman (npr. 1., 2., 3.)")
            col4, col5, col6 = st.columns(3)
            with col4:
                bouts_total = st.number_input("Borbi", min_value=0, value=0, step=1)
            with col5:
                wins = st.number_input("Pobjeda", min_value=0, value=0, step=1)
            with col6:
                losses = st.number_input("Poraza", min_value=0, value=0, step=1)
            metadata = st.text_area("Dodatno (JSON)", value="{}")
            submit_res = st.form_submit_button("Spremi rezultat")
        if submit_res:
            if not comp_map:
                st.error("Prvo unesite natjecanje.")
            elif not athlete:
                st.error("Unesite ime natjecatelja.")
            else:
                comp_id = comp_map.get(competition_label)
                # validate metadata
                try:
                    json.loads(metadata or "{}")
                except Exception as e:
                    st.error(f"Neispravan JSON u 'Dodatno': {e}")
                else:
                    conn.execute(
                        """INSERT INTO competition_results
                        (competition_id, athlete, weight_category, age_group, bouts_total, wins, losses, placement, metadata)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                        (comp_id, athlete, weight_category, r_age_group, int(bouts_total), int(wins), int(losses), placement, metadata or "{}")
                    )
                    conn.commit()
                    st.success("Rezultat spremljen.")

    with tab3:
        st.subheader("Pregled natjecanja i rezultata")
        df_comp = pd.read_sql_query("""
            SELECT id, name, date_from AS datum, city AS grad, country AS drzava, style AS stil,
                   age_group AS uzrast, team_rank AS ekipni_poredak
            FROM competitions ORDER BY date_from DESC
        """, conn)
        st.markdown("**Natjecanja**")
        st.dataframe(df_comp, use_container_width=True)

        st.markdown("---")
        df_res = pd.read_sql_query("""
            SELECT cr.id, c.name AS natjecanje, c.date_from AS datum,
                   cr.athlete AS natjecatelj, cr.weight_category AS kategorija, cr.age_group AS uzrast,
                   cr.bouts_total AS borbi, cr.wins AS pobjeda, cr.losses AS poraza, cr.placement AS plasman
            FROM competition_results cr JOIN competitions c ON c.id=cr.competition_id
            ORDER BY c.date_from DESC, cr.id DESC
        """, conn)
        st.markdown("**Rezultati**")
        st.dataframe(df_res, use_container_width=True)

# ---- Run ----
if __name__ == "__main__":
    section_competitions()
