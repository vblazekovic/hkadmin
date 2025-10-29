
import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import date

st.set_page_config(page_title="HK Podravka Admin", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
DB_PATH = "podravka.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT,
            subtype TEXT,
            date_from TEXT,
            date_to TEXT,
            country TEXT,
            iso_code TEXT,
            ioc_code TEXT,
            place TEXT,
            style TEXT,
            age_group TEXT,
            club_competitors INTEGER,
            team_rank TEXT,
            wins INTEGER,
            losses INTEGER,
            coaches_text TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def show_logo_safe(logo_path_or_url: str | None, caption: str = "", width=None, use_column_width=True):
    if not logo_path_or_url:
        st.warning("Logo nije dostupan.")
        return
    try:
        p = Path(str(logo_path_or_url))
        if p.exists() and p.is_file():
            st.image(str(p), caption=caption, width=width, use_column_width=use_column_width)
            return
        st.image(logo_path_or_url, caption=caption, width=width, use_column_width=use_column_width)
    except Exception as e:
        st.warning(f"Logo nije moguće učitati ({e.__class__.__name__}).")
        if caption:
            st.caption(caption)

def download_df_as_excel_button(df: pd.DataFrame, filename_base: str):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    st.download_button("💾 Preuzmi Excel", data=buf.getvalue(), file_name=f"{filename_base}_{date.today().isoformat()}.xlsx")

def table_exists(conn, name: str) -> bool:
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
        return cur.fetchone() is not None
    except Exception:
        return False

# -----------------------------
# Stats helper
# -----------------------------
def compute_competition_stats(conn, member_id: int | None = None):
    """
    Sažetak natjecanja iz SQLite baze.
    Ako je member_id=None -> statistika kluba.
    Ako je member_id postavljen -> statistika sportaša (uklj. plasman).
    """
    try:
        if member_id is None:
            q = """
                SELECT
                    c.kind AS vrsta_natjecanja,
                    COALESCE(c.subtype,'') AS podvrsta,
                    c.date_from AS datum_od,
                    c.date_to   AS datum_do,
                    c.country   AS država,
                    c.place     AS mjesto,
                    c.style     AS stil,
                    c.age_group AS uzrast,
                    c.club_competitors AS nastupilo_hrvača,
                    c.team_rank AS ekipni_plasman,
                    COALESCE(SUM(cr.wins),0)   AS pobjeda,
                    COALESCE(SUM(cr.losses),0) AS poraza,
                    c.coaches_text AS treneri
                FROM competitions c
                LEFT JOIN competition_results cr ON cr.competition_id = c.id
                GROUP BY c.id
                ORDER BY c.date_from DESC
            """
            df = pd.read_sql_query(q, conn)
        else:
            q = """
                SELECT
                    c.kind AS vrsta_natjecanja,
                    COALESCE(c.subtype,'') AS podvrsta,
                    c.date_from AS datum_od,
                    c.date_to   AS datum_do,
                    c.country   AS država,
                    c.place     AS mjesto,
                    c.style     AS stil,
                    c.age_group AS uzrast,
                    c.club_competitors AS nastupilo_hrvača,
                    c.team_rank AS ekipni_plasman,
                    COALESCE(SUM(cr.wins),0)   AS pobjeda,
                    COALESCE(SUM(cr.losses),0) AS poraza,
                    c.coaches_text AS treneri,
                    MAX(COALESCE(cr.placement,0)) AS plasman
                FROM competitions c
                LEFT JOIN competition_results cr ON cr.competition_id = c.id
                WHERE cr.member_id = ?
                GROUP BY c.id
                ORDER BY c.date_from DESC
            """
            df = pd.read_sql_query(q, conn, params=(int(member_id),))

        if not df.empty:
            try:
                df["datum_od"] = pd.to_datetime(df["datum_od"]).dt.strftime("%d.%m.%Y.")
                df["datum_do"] = pd.to_datetime(df["datum_do"]).dt.strftime("%d.%m.%Y.")
            except Exception:
                pass
        return df
    except Exception as e:
        st.error(f"Greška pri dohvaćanju podataka: {e}")
        return pd.DataFrame()

# -----------------------------
# Sections
# -----------------------------
def section_club():
    st.header("Klub")
    st.text_input("Naziv kluba", key="klub_naziv")
    st.text_input("Adresa", key="klub_adresa")
    st.text_input("OIB", key="klub_oib")
    st.text_input("IBAN", key="klub_iban")
    logo = "https://hk-podravka.com/wp-content/uploads/2021/08/cropped-HK-Podravka-logo.png"
    show_logo_safe(logo, caption="Hrvački klub Podravka")

def section_members():
    st.header("Članovi")
    st.info("Sekcija za članove (postojeća logika ostaje).")

def section_coaches():
    st.header("Treneri")
    st.info("Sekcija za trenere (postojeća logika ostaje).")

def section_stats():
    st.header("Statistika")
    st.info("Sekcija za statistiku (postojeća logika ostaje).")

def section_groups():
    st.header("Grupe")
    st.info("Sekcija za grupe (postojeća logika ostaje).")

def section_veterans():
    st.header("Veterani")
    st.info("Sekcija za veterane (postojeća logika ostaje).")

def section_presence():
    st.header("Prisutstvo")
    st.info("Sekcija za prisutstvo (postojeća logika ostaje).")

def section_competitions():
    st.header("Natjecanja i rezultati")
    conn = get_conn()

    KINDS = [
        "PRVENSTVO HRVATSKE",
        "MEĐUNARODNI TURNIR",
        "REPREZENTATIVNI NASTUP",
        "HRVAČKA LIGA ZA SENIORE",
        "MEĐUNARODNA HRVAČKA LIGA ZA KADETE",
        "REGIONALNO PRVENSTVO",
        "LIGA ZA DJEVOJČICE",
        "OSTALO"
    ]
    REP_SUB = ["PRVENSTVO EUROPE", "PRVENSTVO SVIJETA", "PRVENSTVO BALKANA", "UWW TURNIR", "OSTALO"]
    STYLES = ["GR", "FS", "WW", "BW"]
    AGES = ["POČETNICI", "U11", "U13", "U15", "U17", "U20", "U23", "SENIORI"]

    # Countries with ISO + IOC
    try:
        import pycountry
        COUNTRIES = sorted(
            [(f"{c.name} ({getattr(c, 'alpha_3', '').upper()})",
              getattr(c, "alpha_3", "").lower(),
              getattr(c, "alpha_3", "").upper())
             for c in pycountry.countries],
            key=lambda x: x[0]
        )
    except Exception:
        COUNTRIES = [
            ("Croatia (CRO)", "hrv", "CRO"),
            ("Serbia (SRB)", "srb", "SRB"),
            ("Slovenia (SLO)", "svn", "SLO"),
            ("Bosnia and Herzegovina (BIH)", "bih", "BIH"),
            ("Hungary (HUN)", "hun", "HUN"),
            ("Austria (AUT)", "aut", "AUT"),
            ("Italy (ITA)", "ita", "ITA"),
            ("Germany (GER)", "deu", "GER"),
        ]

    with st.form("competition_form"):
        kind = st.selectbox("Vrsta natjecanja", KINDS, key="comp_kind")
        subtype = ""
        if kind == "REPREZENTATIVNI NASTUP":
            rep_choice = st.selectbox("Podvrsta reprezentativnog nastupa", REP_SUB, key="comp_rep_sub")
            if rep_choice == "OSTALO":
                subtype = st.text_input("Upiši podvrstu reprezentativnog nastupa", key="comp_rep_custom")
            else:
                subtype = rep_choice
        elif kind == "OSTALO":
            subtype = st.text_input("Upiši vrstu (ako 'OSTALO')", key="comp_kind_custom")

        col1, col2 = st.columns(2)
        date_from = col1.date_input("Datum od", value=date.today(), key="comp_date_from")
        date_to = col2.date_input("Datum do", value=date.today(), key="comp_date_to")

        country_names = [c[0] for c in COUNTRIES]
        selected_country = st.selectbox("Država", country_names, key="comp_country")
        iso_code = next(c[1] for c in COUNTRIES if c[0] == selected_country)
        ioc_code = next(c[2] for c in COUNTRIES if c[0] == selected_country)
        st.text_input("ISO3 (auto)", iso_code, disabled=True)
        st.text_input("IOC (auto)", ioc_code, disabled=True)

        place = st.text_input("Mjesto", key="comp_place")
        style = st.selectbox("Hrvački stil", STYLES, key="comp_style")
        age_group = st.selectbox("Uzrast", AGES, key="comp_age")

        col3, col4, col5 = st.columns(3)
        club_competitors = col3.number_input("Broj naših hrvača", min_value=0, step=1, key="comp_hrvaci")
        team_rank = col4.text_input("Ekipni plasman", key="comp_team_rank")

        # Auto wins/losses if competition_results exists
        auto_results = table_exists(conn, "competition_results")
        if auto_results:
            st.info("Broj pobjeda/poraza se računa automatski iz competition_results (ako podaci postoje).")
            wins = 0
            losses = 0
        else:
            col6, col7 = st.columns(2)
            wins = col6.number_input("Ukupan broj pobjeda", min_value=0, step=1, key="comp_wins")
            losses = col7.number_input("Ukupan broj poraza", min_value=0, step=1, key="comp_losses")

        # Coaches list (if table exists)
        coaches = []
        if table_exists(conn, "coaches"):
            try:
                coaches = [r[0] for r in conn.execute("SELECT full_name FROM coaches ORDER BY full_name").fetchall()]
            except Exception:
                coaches = []
        mode = st.radio("Odabir trenera", ["Jedan", "Više"], horizontal=True, key="comp_tr_mode")
        if mode == "Jedan":
            coach_text = st.selectbox("Trener", coaches if coaches else [""], key="comp_tr_one")
        else:
            coach_list = st.multiselect("Treneri", coaches, key="comp_tr_many")
            coach_text = ", ".join(coach_list)

        submit = st.form_submit_button("Spremi natjecanje")

        if submit:
            conn.execute(
                "INSERT INTO competitions (kind, subtype, date_from, date_to, country, iso_code, ioc_code, place, style, age_group, club_competitors, team_rank, wins, losses, coaches_text) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (kind, subtype, str(date_from), str(date_to), selected_country, iso_code, ioc_code, place, style, age_group, int(club_competitors), team_rank, int(wins), int(losses), coach_text),
            )
            conn.commit()
            st.success("Natjecanje spremljeno.")

    # --- Sažetak ispod forme ---
    st.markdown("---")
    st.subheader("Sažetak natjecanja")
    view_mode = st.radio("Prikaz", ["Statistika kluba", "Statistika sportaša"], horizontal=True, key="comp_view_mode")

    if view_mode == "Statistika kluba":
        # Filters
        f1, f2, f3, f4 = st.columns(4)
        year_filter = f1.text_input("Godina (npr. 2025)", key="sum_year")
        style_filter = f2.selectbox("Stil", ["Svi", "GR", "FS", "WW", "BW"], key="sum_style")
        age_filter = f3.selectbox("Uzrast", ["Svi","POČETNICI","U11","U13","U15","U17","U20","U23","SENIORI"], key="sum_age")
        rep_only = f4.checkbox("Samo reprezentativni", key="sum_rep")

        df_stats = compute_competition_stats(conn, None)
        if not df_stats.empty:
            if year_filter:
                df_stats = df_stats[df_stats["datum_od"].str.contains(year_filter)]
            if style_filter != "Svi":
                df_stats = df_stats[df_stats["stil"] == style_filter]
            if age_filter != "Svi":
                df_stats = df_stats[df_stats["uzrast"] == age_filter]
            if rep_only:
                df_stats = df_stats[df_stats["vrsta_natjecanja"] == "REPREZENTATIVNI NASTUP"]
        st.dataframe(df_stats[["vrsta_natjecanja","podvrsta","datum_od","datum_do","država","mjesto","nastupilo_hrvača","ekipni_plasman","pobjeda","poraza","treneri"]], use_container_width=True)
        download_df_as_excel_button(df_stats, "natjecanja_statistika")
    else:
        # Athlete
        if table_exists(conn, "members"):
            members = conn.execute("SELECT id, full_name FROM members ORDER BY full_name").fetchall()
        else:
            members = []
        if members:
            sel = st.selectbox("Sportaš", [f"{m[0]} – {m[1]}" for m in members], key="comp_member_sel")
            mid = int(sel.split(" – ")[0])
            df_stats = compute_competition_stats(conn, mid)
            yf2 = st.text_input("Godina (npr. 2025)", key="sum_year_ath")
            if yf2 and not df_stats.empty:
                df_stats = df_stats[df_stats["datum_od"].str.contains(yf2)]
            cols = ["vrsta_natjecanja","podvrsta","datum_od","datum_do","država","mjesto","nastupilo_hrvača","ekipni_plasman","pobjeda","poraza","treneri","plasman"]
            show_cols = [c for c in cols if c in df_stats.columns]
            st.dataframe(df_stats[show_cols], use_container_width=True)
            download_df_as_excel_button(df_stats, "natjecanja_sportas")
        else:
            st.info("Nema unesenih sportaša.")

# -----------------------------
# App
# -----------------------------
def main():
    init_db()
    with st.sidebar:
        st.title("Hrvački klub Podravka")
        choice = st.radio("Navigacija", ["Klub","Članovi","Treneri","Natjecanja i rezultati","Statistika","Grupe","Veterani","Prisutstvo"], key="nav")

    if choice == "Klub":
        section_club()
    elif choice == "Članovi":
        section_members()
    elif choice == "Treneri":
        section_coaches()
    elif choice == "Natjecanja i rezultati":
        section_competitions()
    elif choice == "Statistika":
        section_stats()
    elif choice == "Grupe":
        section_groups()
    elif choice == "Veterani":
        section_veterans()
    elif choice == "Prisutstvo":
        section_presence()

    # Smoke test
    with st.sidebar:
        st.divider()
        st.caption("Smoke test")
        try:
            conn = get_conn()
            conn.execute("SELECT 1")
            st.success("DB OK")
        except Exception as e:
            st.error(f"Baza greška: {e}")

if __name__ == "__main__":
    main()
