# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import sqlite3, json
from datetime import date, datetime

st.set_page_config("HKP – Hotfix Natjecanja", layout="wide")

# --- DB helpers ---
def get_conn():
    return sqlite3.connect("club.db")

def ensure_tables(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS competitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT, custom_kind TEXT, name TEXT,
        date_from TEXT, date_to TEXT, place TEXT,
        style TEXT, age_group TEXT, country TEXT, country_code TEXT,
        team_rank TEXT, club_competitors INTEGER, total_competitors INTEGER,
        total_clubs INTEGER, total_countries INTEGER, coaches_text TEXT,
        notes TEXT, bulletin_link TEXT, results_link TEXT, gallery_link TEXT,
        bulletin_file TEXT, results_file TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS competition_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id INTEGER, member_id INTEGER,
        weight_category TEXT, age_group TEXT,
        bouts_total INTEGER, wins INTEGER, losses INTEGER,
        placement INTEGER, opponent_list TEXT, notes TEXT
    )""")
    conn.commit()

def save_upload(file, folder):
    if not file: return ""
    import os, pathlib
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    path = os.path.join(folder, file.name)
    with open(path, "wb") as f: f.write(file.getbuffer())
    return path

# --- Fallback COUNTRIES ---
try:
    import pycountry
    COUNTRIES = {c.name: getattr(c, "alpha_3", "") for c in pycountry.countries}
except Exception:
    COUNTRIES = {"Hrvatska":"CRO","Srbija":"SRB","Slovenija":"SVN","Mađarska":"HUN","Italija":"ITA","Njemačka":"DEU","Austrija":"AUT","Francuska":"FRA","Španjolska":"ESP","Švicarska":"CHE","Turska":"TUR","SAD":"USA","Kanada":"CAN","UK":"GBR"}

def page_header(title, subtitle=""):
    st.markdown(f"## {title}")
    if subtitle: st.caption(subtitle)

def app():
    conn = get_conn()
    ensure_tables(conn)

    page_header("Natjecanja i rezultati (HOTFIX)", "Stabilni unos + rezultati bez NameError-a")

    KINDS = [
        "PRVENSTVO HRVATSKE","MEĐUNARODNI TURNIR","REPREZENTATIVNI NASTUP",
        "HRVAČKA LIGA ZA SENIORE","MEĐUNARODNA HRVAČKA LIGA ZA KADETE",
        "REGIONALNO PRVENSTVO","LIGA ZA DJEVOJČICE","OSTALO"
    ]
    REP_SUB = ["PRVENSTVO EUROPE","PRVENSTVO SVIJETA","PRVENSTVO BALKANA","UWW TURNIR"]
    STYLES = ["GR","FS","WW","BW","MODIFICIRANO"]
    AGES = ["POČETNICI","U11","U13","U15","U17","U20","U23","SENIORI"]

    with st.form("comp_form"):
        kind = st.selectbox("Vrsta natjecanja", KINDS)
        rep_sub = st.selectbox("Podvrsta reprezentativnog nastupa", REP_SUB) if kind=="REPREZENTATIVNI NASTUP" else ""
        custom_kind = st.text_input("Upiši vrstu (ako 'OSTALO')", disabled=(kind!="OSTALO"))
        name = st.text_input("Ime natjecanja (ako postoji naziv)")
        c1,c2 = st.columns(2)
        date_from = c1.date_input("Datum od", value=date.today())
        date_to   = c2.date_input("Datum do (ako 1 dan, ostavi isti)", value=date.today())
        place = st.text_input("Mjesto")

        country = st.selectbox("Država", sorted(list(COUNTRIES.keys())))
        country_code = COUNTRIES.get(country, "")
        st.text_input("Kratica države (auto)", value=country_code, disabled=True)

        style = st.selectbox("Hrvački stil", STYLES)
        age_group = st.selectbox("Uzrast", AGES)

        c3,c4,c5 = st.columns(3)
        team_rank = c3.text_input("Ekipni poredak (npr. 1., 5., 10.)")
        club_competitors = c4.number_input("Broj naših natjecatelja", min_value=0, step=1)
        total_competitors = c5.number_input("Ukupan broj natjecatelja", min_value=0, step=1)

        c6,c7 = st.columns(2)
        total_clubs = c6.number_input("Broj klubova", min_value=0, step=1)
        total_countries = c7.number_input("Broj zemalja", min_value=0, step=1)

        notes = st.text_area("Zapažanje trenera (za objave)")
        bulletin_link = st.text_input("Link na bilten/rezultate")
        results_link = st.text_input("Link na službene rezultate")
        gallery_link = st.text_input("Link na objavu na webu (galerija)")
        bulletin_file = st.file_uploader("Učitaj bilten (pdf)", type=["pdf"])
        results_file  = st.file_uploader("Učitaj rezultate (pdf/xlsx)", type=["pdf","xlsx"])

        submit = st.form_submit_button("Spremi natjecanje")

    if submit:
        bull_p = save_upload(bulletin_file, "competitions/docs") if bulletin_file else ""
        res_p  = save_upload(results_file,  "competitions/docs") if results_file  else ""
        conn.execute("""INSERT INTO competitions
            (kind,custom_kind,name,date_from,date_to,place,style,age_group,country,country_code,
             team_rank,club_competitors,total_competitors,total_clubs,total_countries,
             coaches_text,notes,bulletin_link,results_link,gallery_link,bulletin_file,results_file)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (kind, rep_sub if kind=="REPREZENTATIVNI NASTUP" else custom_kind, name,
             str(date_from), str(date_to), f"{place}, {country}", style, age_group, country, country_code,
             team_rank, int(club_competitors), int(total_competitors), int(total_clubs), int(total_countries),
             "", notes, bulletin_link, results_link, gallery_link, bull_p, res_p))
        conn.commit()
        st.success("Natjecanje spremljeno.")

    st.markdown("---")
    st.subheader("Unos rezultata sportaša (plasman, protivnici)")

    comps = conn.execute("SELECT id, name, date_from FROM competitions ORDER BY date_from DESC").fetchall()
    members = conn.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, full_name TEXT)")
    members = conn.execute("SELECT id, full_name FROM members ORDER BY full_name").fetchall()

    if comps and members:
        comp_sel = st.selectbox("Natjecanje", [f"{c[0]} – {c[1]} ({c[2]})" for c in comps])
        mem_sel  = st.multiselect("Sportaši", [f"{m[0]} – {m[1]}" for m in members])

        AGES_ALL = ["POČETNICI","U11","U13","U15","U17","U20","U23","SENIORI"]
        with st.form("add_results2"):
            for idx, ms in enumerate(mem_sel):
                st.markdown(f"**#{idx+1} – {ms.split(' – ')[1]}**")
                cA,cB = st.columns(2)
                weight_cat = cA.text_input("Kategorija", key=f"res_k_{idx}")
                age_g      = cB.selectbox("Uzrast", AGES_ALL, key=f"res_age_{idx}")
                c1,c2,c3 = st.columns(3)
                bouts_total = c1.number_input("Ukupno borbi", min_value=0, step=1, key=f"res_bt_{idx}")
                wins        = c2.number_input("Pobjede", min_value=0, step=1, key=f"res_w_{idx}")
                losses      = c3.number_input("Porazi", min_value=0, step=1, key=f"res_l_{idx}")
                placement   = st.number_input("Plasman (1-100)", min_value=1, max_value=100, step=1, key=f"res_p_{idx}")
                st.caption("Protivnici – dodaj redove po potrebi")
                st.data_editor(pd.DataFrame(columns=["Ime i prezime","Klub"]), use_container_width=True, hide_index=True, num_rows="dynamic", key=f"opp_tbl_{idx}")
                st.text_area("Napomena trenera", key=f"res_note_{idx}")
                st.markdown("---")
            ok = st.form_submit_button("Spremi rezultate")
        if ok:
            cid = int(comp_sel.split(" – ")[0])
            for idx, ms in enumerate(mem_sel):
                mid = int(ms.split(" – ")[0])
                opp_df = st.session_state.get(f"opp_tbl_{idx}")
                opp_list = opp_df.to_dict(orient="records") if isinstance(opp_df, pd.DataFrame) else []
                conn.execute("""INSERT INTO competition_results
                    (competition_id,member_id,weight_category,age_group,bouts_total,wins,losses,placement,opponent_list,notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""", (
                        cid, mid, st.session_state.get(f"res_k_{idx}",""),
                        st.session_state.get(f"res_age_{idx}",""),
                        int(st.session_state.get(f"res_bt_{idx}",0) or 0),
                        int(st.session_state.get(f"res_w_{idx}",0) or 0),
                        int(st.session_state.get(f"res_l_{idx}",0) or 0),
                        int(st.session_state.get(f"res_p_{idx}",0) or 0),
                        json.dumps(opp_list, ensure_ascii=False),
                        st.session_state.get(f"res_note_{idx}","")
                ))
            conn.commit()
            st.success("Rezultati spremljeni.")

    st.markdown("---")
    st.subheader("Pregled rezultata")
    try:
        df = pd.read_sql_query("""
            SELECT cr.id, c.name AS natjecanje, c.date_from AS datum,
                   cr.weight_category AS kategorija, cr.age_group AS uzrast,
                   cr.bouts_total AS borbi, cr.wins AS pobjeda, cr.losses AS poraza, cr.placement AS plasman
            FROM competition_results cr JOIN competitions c ON c.id=cr.competition_id
            ORDER BY c.date_from DESC
        """, get_conn())
    except Exception:
        df = pd.DataFrame()
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    app()
