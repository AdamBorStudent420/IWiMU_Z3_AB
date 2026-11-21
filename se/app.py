"""Interfejs systemu ekspertowego — do uzupełnienia na spotkaniu 3. Uruchom: streamlit run app.py"""
import sys
#from silnik import coto
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "silnik.py"))
from silnik import coto, wczytaj_baze, wnioskuj_w_przod, wyjasnij_jak  # noqa: E402
from weryfikacja import weryfikuj  # noqa: E402

PLIK_BAZY = Path(__file__).parent.parent / "wiedza" / "rowery.json"  # TODO 1: podmień na swoją bazę
baza = wczytaj_baze(PLIK_BAZY)

st.set_page_config(page_title=baza["nazwa"])
st.title(baza["nazwa"])

with st.sidebar:
    st.header("Weryfikacja bazy wiedzy")
    raport = weryfikuj(baza)
    if not raport:
        st.success("Nie wykryto problemów.")
    for poziom, komunikat in raport:
        (st.error if poziom == "BŁĄD" else st.warning)(komunikat)

with st.form("konsultacja"):
    fakty = {}
    for nazwa, opis in baza["atrybuty"].items():
        if opis["typ"] == "liczba":
            lo, hi = opis.get("zakres", [-100, 100])
            fakty[nazwa] = st.slider(opis["pytanie"], lo, hi, (lo + hi) // 2)
        # TODO 2: dla typu "wybor" dodaj st.radio z listą opis["wartosci"]
        elif opis["typ"] == "wybor":
            fakty[nazwa] = st.radio(opis["pytanie"], opis["wartosci"])
    wyslano = st.form_submit_button("Doradź")

if wyslano:
    wynik, slad = wnioskuj_w_przod(baza, fakty)
    cel = wynik.get(baza["cel"])
    # TODO 3: jeśli cel is None — st.error z informacją, że brakuje reguły;
    #         w przeciwnym razie st.success z wynikiem i st.info z opisem coto(baza, slad).
    if cel is None:
        st.error("Nie udało się wyznaczyć wyniku — brakuje odpowiedniej reguły w bazie wiedzy.")
    else:
        st.success(f"Polecam: **{cel}**")
        opis = coto(baza, slad)
        if opis:
            st.info(opis)
    # TODO 4: w st.expander("Jak do tego doszedłem?") wypisz kroki z wyjasnij_jak(baza, slad).
    with st.expander("Jak do tego doszedłem?"):
        kroki = wyjasnij_jak(baza, slad)
        if kroki:
            for krok in kroki:
                st.write(krok)
        else:
            st.write("Nie odpalono żadnej reguły.")
