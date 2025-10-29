
import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="HK Podravka Admin", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
class KeyGen:
    """
    Deterministic, section-scoped key generator.
    Use like: key = keys("year")  -> returns "treneri_year" (stable across reruns)
    Ensures we never reuse the same element_id across different sections/forms.
    """
    def __init__(self, scope: str):
        self.scope = scope

    def __call__(self, name: str) -> str:
        return f"{self.scope}_{name}"

def section_header(title: str, subtitle: str | None = None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()

# -----------------------------
# Sections
# -----------------------------
def section_klub():
    keys = KeyGen("klub")
    section_header("Klub", "Osnovne informacije o klubu")
    st.text_input("Naziv kluba", key=keys("naziv"))
    st.text_input("Adresa", key=keys("adresa"))
    st.text_input("OIB", key=keys("oib"))
    st.text_input("IBAN", key=keys("iban"))
    st.text_input("Web", key=keys("web"))
    st.text_input("E-mail", key=keys("email"))
    with st.expander("Napomena"):
        st.text_area("Bilješka", key=keys("napomena"))

def section_clanovi():
    keys = KeyGen("clanovi")
    section_header("Članovi", "Upravljanje članovima")
    with st.form(key=keys("form_novi_clan")):
        st.text_input("Ime", key=keys("ime"))
        st.text_input("Prezime", key=keys("prezime"))
        st.date_input("Datum rođenja", key=keys("dob"))
        st.selectbox("Spol", ["M", "Ž"], key=keys("spol"))
        submitted = st.form_submit_button("Dodaj člana", use_container_width=True)
        if submitted:
            st.success("Član dodan.")

    st.text_input("Pretraži člana", key=keys("search"))
    st.dataframe({"Ime": [], "Prezime": [], "Godina": []})

def section_treneri():
    keys = KeyGen("treneri")
    section_header("Treneri", "Upravljanje trenerima")
    with st.form(key=keys("form_trener")):
        # !!! Important: label strings may repeat across the app,
        # but KEYS are unique per section so no DuplicateElementId.
        st.text_input("Ime", key=keys("ime"))
        st.text_input("Prezime", key=keys("prezime"))
        st.text_input("Godina (npr. 2025)", key=keys("godina"))
        st.text_input("Kontakt", key=keys("kontakt"))
        ok = st.form_submit_button("Spremi trenera", use_container_width=True)
        if ok:
            st.success("Trener spremljen.")

    with st.expander("Lista trenera"):
        st.dataframe({"Ime": [], "Prezime": [], "Kontakt": []})

def section_natjecanja_i_rezultati():
    keys = KeyGen("natjecanja")
    section_header("Natjecanja i rezultati", "Evidencija natjecanja")
    with st.form(key=keys("form_natjecanje")):
        st.text_input("Naziv natjecanja", key=keys("naziv"))
        st.text_input("Lokacija", key=keys("lokacija"))
        st.date_input("Datum", key=keys("datum"))
        # This label appears in other sections too, but key is unique here:
        st.text_input("Godina (npr. 2025)", key=keys("godina"))
        st.text_area("Rezultati (sažetak)", key=keys("rezultati"))
        ok = st.form_submit_button("Spremi natjecanje", use_container_width=True)
        if ok:
            st.success("Natjecanje spremljeno.")

    st.text_input("Pretraži natjecanja", key=keys("search"))
    st.dataframe({"Naziv": [], "Datum": [], "Lokacija": []})

def section_statistika():
    keys = KeyGen("statistika")
    section_header("Statistika", "Osnovne metrike")
    kol1, kol2, kol3 = st.columns(3)
    with kol1:
        st.metric("Broj članova", 0)
    with kol2:
        st.metric("Broj trenera", 0)
    with kol3:
        st.metric("Natjecanja (godina)", 0)
    st.text_input("Godina (npr. 2025)", key=keys("godina_filter"))

def section_grupe():
    keys = KeyGen("grupe")
    section_header("Grupe", "Trenažne grupe")
    with st.form(key=keys("form_grupa")):
        st.text_input("Naziv grupe", key=keys("naziv"))
        st.selectbox("Trener", ["—"], key=keys("trener"))
        st.number_input("Broj članova", min_value=0, key=keys("broj"))
        ok = st.form_submit_button("Spremi grupu", use_container_width=True)
        if ok:
            st.success("Grupa spremljena.")
    st.dataframe({"Grupa": [], "Trener": [], "Broj članova": []})

def section_veterani():
    keys = KeyGen("veterani")
    section_header("Veterani", "Program za veterane")
    st.text_input("Pretraži veterane", key=keys("search"))
    with st.expander("Dodaj veterana"):
        st.text_input("Ime", key=keys("ime"))
        st.text_input("Prezime", key=keys("prezime"))
        st.text_input("Kontakt", key=keys("kontakt"))

def section_prisutstvo():
    keys = KeyGen("prisutstvo")
    section_header("Prisutstvo", "Evidencija treninga")
    st.date_input("Datum treninga", key=keys("datum"))
    st.multiselect("Članovi", [], key=keys("clanovi"))
    st.button("Spremi prisutnost", key=keys("spremi"))

# -----------------------------
# Router / Sidebar
# -----------------------------
MENU = [
    "Klub",
    "Članovi",
    "Treneri",
    "Natjecanja i rezultati",
    "Statistika",
    "Grupe",
    "Veterani",
    "Prisutstvo",
]

with st.sidebar:
    st.title("Hrvački klub Podravka")
    choice = st.radio("Navigacija", MENU, key="nav")

def main():
    if choice == "Klub":
        section_klub()
    elif choice == "Članovi":
        section_clanovi()
    elif choice == "Treneri":
        section_treneri()
    elif choice == "Natjecanja i rezultati":
        section_natjecanja_i_rezultati()
    elif choice == "Statistika":
        section_statistika()
    elif choice == "Grupe":
        section_grupe()
    elif choice == "Veterani":
        section_veterani()
    elif choice == "Prisutstvo":
        section_prisutstvo()
    else:
        st.info("Odaberite stavku iz izbornika.")

if __name__ == "__main__":
    main()
