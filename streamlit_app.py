
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# OPTIONAL dependency; app radi i bez pycountry, ali lista država tada neće biti puna
try:
    import pycountry
except Exception:
    pycountry = None

st.set_page_config(page_title="HK Podravka – Klupska aplikacija", layout="wide")

# ==============================
# DB helper
# ==============================
def get_conn():
    conn = sqlite3.connect("club.db", check_same_thread=False)
    # Minimalni skup tablica (ostale sekcije zadržane kako su bile u tvojoj verziji)
    conn.execute("""CREATE TABLE IF NOT EXISTS club_info(
        id INTEGER PRIMARY KEY CHECK (id=1),
        name TEXT, address TEXT, contact TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT, dob TEXT, is_veteran INTEGER DEFAULT 0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS coaches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT UNIQUE
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS competitions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT,
        custom_kind TEXT,
        name TEXT,
        date_from TEXT,
        date_to TEXT,
        place TEXT,
        style TEXT,
        age_group TEXT,
        country TEXT,
        country_code TEXT,
        team_rank TEXT,
        club_competitors INTEGER,
        total_competitors INTEGER,
        total_clubs INTEGER,
        total_countries INTEGER,
        coaches_text TEXT,
        notes TEXT,
        bulletin_link TEXT,
        results_link TEXT,
        gallery_link TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS competition_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id INTEGER,
        member_id INTEGER,
        weight_category TEXT,
        style TEXT,
        placing TEXT,
        result_text TEXT
    )""")
    return conn

conn = get_conn()

# ==============================
# Utils
# ==============================
KINDS = [
    "PRVENSTVO HRVATSKE",
    "MEĐUNARODNI TURNIR",
    "REPREZENTATIVNI NASTUP",
    "HRVAČKA LIGA ZA SENIORE",
    "MEĐUNARODNA HRVAČKA LIGA ZA KADETE",
    "REGIONALNO PRVENSTVO",
    "LIGA ZA DJEVOJČICE",
    "OSTALO",
]
REP_SUB = ["PRVENSTVO EUROPE", "PRVENSTVO SVIJETA", "PRVENSTVO BALKANA", "UWW TURNIR"]
STYLES = ["GR", "FS", "WW", "BW", "MODIFICIRANO"]
AGES = ["POČETNICI", "U11", "U13", "U15", "U17", "U20", "U23", "SENIORI"]

def all_countries_list():
    if pycountry is None:
        return []
    try:
        return sorted([c.name for c in pycountry.countries])
    except Exception:
        return []

def iso3(name: str) -> str:
    if not name or pycountry is None:
        return ""
    try:
        c = pycountry.countries.get(name=name)
        if c:
            return c.alpha_3
        # fuzzy
        from difflib import get_close_matches
        names = [x.name for x in pycountry.countries]
        m = get_close_matches(name, names, n=1, cutoff=0.7)
        if m:
            c = pycountry.countries.get(name=m[0])
            return c.alpha_3 if c else ""
    except Exception:
        pass
    return ""

def fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return pd.to_datetime(s).strftime("%d.%m.%Y.")
    except Exception:
        return s

# ==============================
# Sidebar (zadržano – možeš mijenjati redoslijed)
# ==============================
menu = st.sidebar.radio(
    "Sekcije",
    ["Klub", "Članstvo", "Prisustvo", "Treneri", "Veterani", "Natjecanja i rezultati", "Izvješća"]
)

# ==============================
# KLUB (ostavljeno jednostavno da se ne dira tvoj postojeći raspored)
# ==============================
if menu == "Klub":
    st.header("Klub")
    row = conn.execute("SELECT name, address, contact FROM club_info WHERE id=1").fetchone()
    name, address, contact = (row if row else ("", "", ""))
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Naziv kluba", value=name or "")
        address = st.text_input("Adresa", value=address or "")
        contact = st.text_input("Kontakt", value=contact or "")
    if st.button("Spremi podatke kluba"):
        conn.execute("INSERT OR REPLACE INTO club_info(id, name, address, contact) VALUES(1,?,?,?)",
                     (name, address, contact))
        conn.commit()
        st.success("Spremljeno.")

# ==============================
# ČLANSTVO (ostavljeno jednostavno)
# ==============================
elif menu == "Članstvo":
    st.header("Članstvo")
    with st.form("m_form"):
        full_name = st.text_input("Ime i prezime")
        dob = st.date_input("Datum rođenja", value=date(2010, 1, 1))
        is_veteran = st.checkbox("Veteran")
        ok = st.form_submit_button("Dodaj")
    if ok and full_name.strip():
        conn.execute(
            "INSERT INTO members(full_name, dob, is_veteran) VALUES(?,?,?)",
            (full_name.strip(), str(dob), 1 if is_veteran else 0),
        )
        conn.commit()
        st.success("Član dodan.")

    dfm = pd.read_sql_query(
        "SELECT id, full_name AS Ime, dob AS Rođen, CASE WHEN is_veteran=1 THEN 'DA' ELSE 'NE' END AS Veteran FROM members ORDER BY full_name",
        conn,
    )
    if not dfm.empty:
        dfm["Rođen"] = dfm["Rođen"].apply(fmt_date)
    st.dataframe(dfm, use_container_width=True)

# ==============================
# PRISUSTVO (placeholder – ne diramo logiku)
# ==============================
elif menu == "Prisustvo":
    st.header("Prisustvo")
    st.info("Sekcija prisustva ostavljena kao u tvojoj verziji (po potrebi dodati tablice & filtre).")

# ==============================
# TRENERI
# ==============================
elif menu == "Treneri":
    st.header("Treneri")
    with st.form("coach_form"):
        cname = st.text_input("Ime i prezime trenera")
        addc = st.form_submit_button("Dodaj trenera")
    if addc and cname.strip():
        try:
            conn.execute("INSERT INTO coaches(full_name) VALUES(?)", (cname.strip(),))
            conn.commit()
            st.success("Trener dodan.")
        except sqlite3.IntegrityError:
            st.warning("Trener već postoji.")
    cdf = pd.read_sql_query("SELECT id, full_name AS Trener FROM coaches ORDER BY full_name", conn)
    st.dataframe(cdf, use_container_width=True)

# ==============================
# VETERANI (placeholder – čita iz members.is_veteran)
# ==============================
elif menu == "Veterani":
    st.header("Veterani")
    vdf = pd.read_sql_query("SELECT full_name AS Ime, dob AS Rođen FROM members WHERE is_veteran=1 ORDER BY full_name", conn)
    if not vdf.empty:
        vdf["Rođen"] = vdf["Rođen"].apply(fmt_date)
    st.dataframe(vdf, use_container_width=True)

# ==============================
# NATJECANJA I REZULTATI — SVE TRAŽENE FUNKCIJE
# ==============================
elif menu == "Natjecanja i rezultati":
    st.header("Natjecanja i rezultati")

    # ---------- Unos natjecanja ----------
    st.subheader("Unos natjecanja")
    with st.form("comp_form"):
        r1c1, r1c2, r1c3 = st.columns([2, 2, 2])
        with r1c1:
            kind = st.selectbox("Vrsta natjecanja", KINDS, key="kind_add")
        with r1c2:
            rep_enabled = (kind == "REPREZENTATIVNI NASTUP")
            rep_sub = st.selectbox("Podvrsta (REP)", REP_SUB, disabled=not rep_enabled, key="rep_add")
        with r1c3:
            custom_kind = st.text_input("Upiši vrstu (ako 'OSTALO')", disabled=(kind != "OSTALO"))

        name = st.text_input("Ime natjecanja (ako postoji)")
        d1, d2 = st.columns(2)
        date_from = d1.date_input("Datum od", value=date.today())
        date_to = d2.date_input("Datum do", value=date.today())
        place = st.text_input("Mjesto (grad)")

        # Države svijeta + ISO3 auto
        countries = all_countries_list()
        ccol, icol = st.columns([3, 1])
        with ccol:
            country = st.selectbox("Država (odaberi)", [""] + countries, index=0)
        with icol:
            iso = iso3(country) if country else ""
            st.text_input("ISO3", value=iso, disabled=True)

        style = st.selectbox("Hrvački stil", STYLES)
        age_group = st.selectbox("Uzrast", AGES)

        n1, n2, n3 = st.columns(3)
        team_rank = n1.text_input("Ekipni poredak (npr. 1., 5., 10.)")
        club_competitors = n2.number_input("Broj naših natjecatelja", min_value=0, step=1, value=0)
        total_competitors = n3.number_input("Ukupan broj natjecatelja", min_value=0, step=1, value=0)

        n4, n5 = st.columns(2)
        total_clubs = n4.number_input("Broj klubova", min_value=0, step=1, value=0)
        total_countries = n5.number_input("Broj zemalja", min_value=0, step=1, value=0)

        # Treneri — multiselect iz baze + dodatni unos (auto insert)
        coach_rows = conn.execute("SELECT full_name FROM coaches ORDER BY full_name").fetchall()
        coach_choices = [r[0] for r in coach_rows] if coach_rows else []
        tc1, tc2 = st.columns([2, 1])
        with tc1:
            coach_mult = st.multiselect("Trener(i) iz baze", coach_choices)
        with tc2:
            coach_custom = st.text_input("Dodatni trener (ime i prezime)")
        coach_all = [c for c in (coach_mult + ([coach_custom] if coach_custom else [])) if c]
        for cname in coach_all:
            if cname not in coach_choices:
                try:
                    conn.execute("INSERT INTO coaches(full_name) VALUES(?)", (cname,))
                    conn.commit()
                except sqlite3.IntegrityError:
                    pass
        coaches_text = ", ".join(coach_all)

        notes = st.text_area("Zapažanje trenera (za objave)")
        bulletin_link = st.text_input("Link na bilten/rezultate")
        results_link = st.text_input("Link na službene rezultate")
        gallery_link = st.text_input("Link na objavu / galeriju")

        submit_comp = st.form_submit_button("Spremi natjecanje")

    if submit_comp:
        conn.execute(
            """INSERT INTO competitions
               (kind, custom_kind, name, date_from, date_to, place, style, age_group,
                country, country_code, team_rank, club_competitors, total_competitors,
                total_clubs, total_countries, coaches_text, notes, bulletin_link, results_link, gallery_link)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                kind,
                rep_sub if kind == "REPREZENTATIVNI NASTUP" else custom_kind,
                name,
                str(date_from),
                str(date_to),
                f"{place}, {country}" if country else place,
                style,
                age_group,
                country,
                iso,
                int(team_rank.split('.')[0]) if team_rank.strip().endswith('.') and team_rank[:-1].isdigit() else team_rank,
                int(club_competitors),
                int(total_competitors),
                int(total_clubs),
                int(total_countries),
                coaches_text,
                notes,
                bulletin_link,
                results_link,
                gallery_link,
            ),
        )
        conn.commit()
        st.success("Natjecanje spremljeno.")

    st.markdown("---")
    # ---------- Uredi / briši / dupliciraj natjecanje ----------
    st.subheader("Uredi / briši / dupliciraj natjecanje")
    comp_rows = pd.read_sql_query(
        "SELECT id, name, date_from, kind FROM competitions ORDER BY date_from DESC", conn
    )
    comp_options = [""] + [f"{r.id} – {r.date_from or ''} – {r.name or ''} ({r.kind or ''})" for _, r in comp_rows.iterrows()]
    pick = st.selectbox("Odaberi natjecanje", comp_options, key="pick_comp_edit")

    if pick:
        edit_id = int(pick.split(" – ")[0])
        rec = pd.read_sql_query(
            """SELECT * FROM competitions WHERE id=?""", conn, params=(edit_id,)
        ).iloc[0]

        with st.form("edit_comp_form"):
            e1, e2, e3 = st.columns([2, 2, 2])
            with e1:
                kind_e = st.selectbox("Vrsta natjecanja", KINDS, index=KINDS.index(rec["kind"]) if rec["kind"] in KINDS else 0, key="kind_e")
            with e2:
                rep_enabled_e = (kind_e == "REPREZENTATIVNI NASTUP")
                rep_sub_e = st.selectbox("Podvrsta (REP)", REP_SUB, disabled=not rep_enabled_e, key="rep_e")
            with e3:
                custom_kind_e = st.text_input("Upiši vrstu (ako 'OSTALO')", value=rec["custom_kind"] or "", disabled=(kind_e != "OSTALO"))

            name_e = st.text_input("Ime natjecanja", value=rec["name"] or "")
            de1, de2 = st.columns(2)
            df_e = de1.date_input("Datum od", value=pd.to_datetime(rec["date_from"]).date() if rec["date_from"] else date.today())
            dt_e = de2.date_input("Datum do", value=pd.to_datetime(rec["date_to"]).date() if rec["date_to"] else date.today())
            place_city = (rec["place"] or "").split(",")[0].strip()
            place_e = st.text_input("Mjesto (grad)", value=place_city)

            # Država + ISO3
            countries = all_countries_list()
            dc1, dc2 = st.columns([3, 1])
            with dc1:
                ci = ([""] + countries).index(rec["country"]) if rec["country"] in countries else 0
                country_e = st.selectbox("Država (odaberi)", [""] + countries, index=ci)
            with dc2:
                iso_e = iso3(country_e) if country_e else (rec["country_code"] or "")
                st.text_input("ISO3", value=iso_e, disabled=True)

            style_e = st.selectbox("Hrvački stil", STYLES, index=STYLES.index(rec["style"]) if rec["style"] in STYLES else 0)
            age_e = st.selectbox("Uzrast", AGES, index=AGES.index(rec["age_group"]) if rec["age_group"] in AGES else 0)

            ee1, ee2, ee3 = st.columns(3)
            team_rank_e = ee1.text_input("Ekipni poredak", value=rec["team_rank"] or "")
            club_comp_e = ee2.number_input("Broj naših natjecatelja", min_value=0, step=1, value=int(rec["club_competitors"] or 0))
            total_comp_e = ee3.number_input("Ukupan broj natjecatelja", min_value=0, step=1, value=int(rec["total_competitors"] or 0))

            ee4, ee5 = st.columns(2)
            total_clubs_e = ee4.number_input("Broj klubova", min_value=0, step=1, value=int(rec["total_clubs"] or 0))
            total_countries_e = ee5.number_input("Broj zemalja", min_value=0, step=1, value=int(rec["total_countries"] or 0))

            # Treneri – multiselect + dodatni
            coach_rows = conn.execute("SELECT full_name FROM coaches ORDER BY full_name").fetchall()
            coach_choices = [r[0] for r in coach_rows] if coach_rows else []
            preselected = [c for c in (rec["coaches_text"] or "").split(", ") if c in coach_choices]
            tc1, tc2 = st.columns([2, 1])
            with tc1:
                coach_mult_e = st.multiselect("Trener(i) iz baze", coach_choices, default=preselected)
            with tc2:
                coach_custom_e = st.text_input("Dodatni trener (ime i prezime)")
            coach_all_e = [c for c in (coach_mult_e + ([coach_custom_e] if coach_custom_e else [])) if c]
            for cname in coach_all_e:
                if cname not in coach_choices:
                    try:
                        conn.execute("INSERT INTO coaches(full_name) VALUES(?)", (cname,))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        pass
            coaches_text_e = ", ".join(coach_all_e) if coach_all_e else (rec["coaches_text"] or "")

            notes_e = st.text_area("Zapažanje trenera (za objave)", value=rec["notes"] or "")
            bull_e = st.text_input("Link na bilten/rezultate", value=rec["bulletin_link"] or "")
            res_e = st.text_input("Link na službene rezultate", value=rec["results_link"] or "")
            gal_e = st.text_input("Link na objavu / galeriju", value=rec["gallery_link"] or "")

            submit_edit = st.form_submit_button("Spremi izmjene")

        if submit_edit:
            conn.execute(
                """UPDATE competitions SET
                   kind=?, custom_kind=?, name=?, date_from=?, date_to=?, place=?, style=?, age_group=?,
                   country=?, country_code=?, team_rank=?, club_competitors=?, total_competitors=?,
                   total_clubs=?, total_countries=?, coaches_text=?, notes=?, bulletin_link=?, results_link=?, gallery_link=?
                   WHERE id=?""",
                (
                    kind_e,
                    rep_sub_e if kind_e == "REPREZENTATIVNI NASTUP" else custom_kind_e,
                    name_e,
                    str(df_e),
                    str(dt_e),
                    f"{place_e}, {country_e}" if country_e else place_e,
                    style_e,
                    age_e,
                    country_e,
                    iso_e,
                    team_rank_e,
                    int(club_comp_e),
                    int(total_comp_e),
                    int(total_clubs_e),
                    int(total_countries_e),
                    coaches_text_e,
                    notes_e,
                    bull_e,
                    res_e,
                    gal_e,
                    edit_id,
                ),
            )
            conn.commit()
            st.success("Natjecanje ažurirano.")

        cdel, cdup = st.columns(2)
        with cdel:
            confirm = st.checkbox("Potvrdi brisanje", key=f"confirm_{edit_id}")
            if st.button("Obriši natjecanje", key=f"del_{edit_id}"):
                if confirm:
                    conn.execute("DELETE FROM competition_results WHERE competition_id=?", (edit_id,))
                    conn.execute("DELETE FROM competitions WHERE id=?", (edit_id,))
                    conn.commit()
                    st.success("Natjecanje obrisano.")
                else:
                    st.warning("Označi potvrdu za brisanje.")
        with cdup:
            if st.button("Dupliciraj u novi zapis", key=f"dup_{edit_id}"):
                conn.execute(
                    """INSERT INTO competitions
                       (kind, custom_kind, name, date_from, date_to, place, style, age_group, country, country_code,
                        team_rank, club_competitors, total_competitors, total_clubs, total_countries,
                        coaches_text, notes, bulletin_link, results_link, gallery_link)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        rec["kind"],
                        rec["custom_kind"],
                        (rec["name"] or "") + " (kopija)",
                        rec["date_from"],
                        rec["date_to"],
                        rec["place"],
                        rec["style"],
                        rec["age_group"],
                        rec["country"],
                        rec["country_code"],
                        rec["team_rank"],
                        rec["club_competitors"],
                        rec["total_competitors"],
                        rec["total_clubs"],
                        rec["total_countries"],
                        rec["coaches_text"],
                        rec["notes"],
                        rec["bulletin_link"],
                        rec["results_link"],
                        rec["gallery_link"],
                    ),
                )
                conn.commit()
                st.success("Kopija napravljena.")

    st.markdown("---")
    # ---------- Unos rezultata sportaša ----------
    st.subheader("Unos rezultata sportaša")
    comps = pd.read_sql_query(
        "SELECT id, name || ' ' || IFNULL(date_from,'') AS naziv FROM competitions ORDER BY date_from DESC",
        conn,
    )
    mems = pd.read_sql_query("SELECT id, full_name AS ime FROM members ORDER BY full_name", conn)
    if comps.empty or mems.empty:
        st.info("Za unos rezultata treba barem jedno natjecanje i jedan član.")
    else:
        rr1, rr2, rr3, rr4 = st.columns(4)
        with rr1:
            comp_sel = st.selectbox("Natjecanje", comps["naziv"].tolist())
            comp_id = int(comps.loc[comps["naziv"] == comp_sel, "id"].values[0])
        with rr2:
            mem_sel = st.selectbox("Sportaš", mems["ime"].tolist())
            member_id = int(mems.loc[mems["ime"] == mem_sel, "id"].values[0])
        with rr3:
            weight_cat = st.text_input("Težinska kategorija (npr. 65kg)")
        with rr4:
            style_r = st.selectbox("Stil", STYLES, index=0, key="style_res_add")

        rcp = st.columns(2)
        placing = rcp[0].text_input("Plasman (npr. 1., 3., 5.)")
        result_text = rcp[1].text_input("Rezime (IP, DQ, 2-1, itd.)")

        if st.button("Dodaj rezultat"):
            conn.execute(
                """INSERT INTO competition_results(competition_id, member_id, weight_category, style, placing, result_text)
                   VALUES (?,?,?,?,?,?)""",
                (comp_id, member_id, weight_cat, style_r, placing, result_text),
            )
            conn.commit()
            st.success("Rezultat dodan.")

    st.markdown("---")
    # ---------- Uredi / obriši rezultate (pojedinačno) ----------
    st.subheader("Uredi / obriši rezultate")
    comps_e = pd.read_sql_query(
        "SELECT id, name || ' ' || IFNULL(date_from,'') AS naziv FROM competitions ORDER BY date_from DESC",
        conn,
    )
    mems_all = pd.read_sql_query("SELECT id, full_name AS ime FROM members ORDER BY full_name", conn)
    if comps_e.empty:
        st.info("Nema natjecanja.")
    else:
        comp_name_e = st.selectbox("Natjecanje", comps_e["naziv"].tolist(), key="res_edit_comp")
        comp_id_e = int(comps_e.loc[comps_e["naziv"] == comp_name_e, "id"].values[0])

        rdf = pd.read_sql_query(
            """
            SELECT r.id, r.member_id, m.full_name AS sportas, r.weight_category, r.style, r.placing, r.result_text
            FROM competition_results r
            JOIN members m ON r.member_id = m.id
            WHERE r.competition_id = ?
            ORDER BY m.full_name
            """,
            conn,
            params=(comp_id_e,),
        )
        if rdf.empty:
            st.info("Nema unesenih rezultata za ovo natjecanje.")
        else:
            imena = mems_all["ime"].tolist()
            for _, rowr in rdf.iterrows():
                rid = int(rowr["id"])
                title = f"#{rid} – {rowr['sportas']} • {rowr['weight_category'] or ''} • {rowr['placing'] or ''}"
                with st.expander(title):
                    c1, c2 = st.columns(2)
                    with c1:
                        try:
                            idx_default = imena.index(rowr["sportas"])
                        except ValueError:
                            idx_default = 0
                        mem_name_e = st.selectbox("Sportaš", imena, index=idx_default, key=f"mem_{rid}")
                        mem_id_e = int(mems_all.loc[mems_all["ime"] == mem_name_e, "id"].values[0])
                        w_e = st.text_input("Težinska kategorija", value=rowr["weight_category"] or "", key=f"w_{rid}")
                        p_e = st.text_input("Plasman", value=rowr["placing"] or "", key=f"pl_{rid}")
                    with c2:
                        st_e = st.selectbox(
                            "Stil", STYLES, index=(STYLES.index(rowr["style"]) if rowr["style"] in STYLES else 0), key=f"st_{rid}"
                        )
                        rx_e = st.text_input("Rezime", value=rowr["result_text"] or "", key=f"rx_{rid}")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Spremi izmjene", key=f"save_{rid}"):
                            conn.execute(
                                """UPDATE competition_results
                                   SET member_id=?, weight_category=?, style=?, placing=?, result_text=?
                                   WHERE id=?""",
                                (mem_id_e, w_e, st_e, p_e, rx_e, rid),
                            )
                            conn.commit()
                            st.success("Rezultat ažuriran.")
                    with b2:
                        if st.button("Obriši rezultat", key=f"del_{rid}"):
                            conn.execute("DELETE FROM competition_results WHERE id=?", (rid,))
                            conn.commit()
                            st.warning("Rezultat obrisan.")

    st.markdown("---")
    # ---------- Pregled i pretraga natjecanja ----------
    st.subheader("Pregled i pretraga natjecanja")
    f = st.columns(6)
    f_kind = f[0].selectbox("Vrsta", [""] + KINDS, index=0)
    with f[1]:
        rep_enabled_filter = (f_kind == "REPREZENTATIVNI NASTUP")
        f_rep_sub = st.selectbox("Podvrsta (REP)", [""] + REP_SUB, index=0, disabled=not rep_enabled_filter)
    f_year = f[2].text_input("Godina (npr. 2025)")
    f_age = f[3].text_input("Uzrast (dio naziva)")
    f_style = f[4].text_input("Stil (GR/FS/WW/BW/MOD)")
    f_country = f[5].text_input("Država (dio naziva)")

    q = """
        SELECT id, name AS Ime, kind AS Vrsta, age_group AS Uzrast, style AS Stil,
               date_from AS Od, date_to AS Do, place AS Mjesto, country AS Država, country_code AS ISO3,
               club_competitors AS Nastupili, coaches_text AS Trener
        FROM competitions WHERE 1=1
    """
    params = []
    if f_kind.strip():
        q += " AND kind = ?"; params.append(f_kind)
    if f_year.strip():
        q += " AND date_from LIKE ?"; params.append(f"{f_year}%")
    if f_age.strip():
        q += " AND age_group LIKE ?"; params.append(f"%{f_age}%")
    if f_style.strip():
        q += " AND style LIKE ?"; params.append(f"%{f_style}%")
    if f_country.strip():
        q += " AND country LIKE ?"; params.append(f"%{f_country}%")
    if f_kind.strip() == "REPREZENTATIVNI NASTUP" and f_rep_sub.strip():
        q += " AND custom_kind = ?"; params.append(f_rep_sub)
    q += " ORDER BY date_from DESC"

    table = pd.read_sql_query(q, conn, params=params)
    if not table.empty:
        table["Od"] = table["Od"].apply(fmt_date)
        table["Do"] = table["Do"].apply(fmt_date)
        table.insert(0, "R.br.", range(1, len(table) + 1))
    st.dataframe(table, use_container_width=True)

# ==============================
# IZVJEŠĆA (placeholder)
# ==============================
elif menu == "Izvješća":
    st.header("Izvješća")
    stats = {
        "Članova": conn.execute("SELECT COUNT(*) FROM members").fetchone()[0],
        "Natjecanja": conn.execute("SELECT COUNT(*) FROM competitions").fetchone()[0],
        "Rezultata": conn.execute("SELECT COUNT(*) FROM competition_results").fetchone()[0],
    }
    st.table(pd.DataFrame(list(stats.items()), columns=["Metrija", "Vrijednost"]))

