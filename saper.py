"""Klasyczna gra Saper napisana w języku Python v3.6"""

import tkinter as tk
from tkinter import messagebox
import random, os, sys


# Ustawienia gry
LICZBA_WIERSZY = 9
LICZBA_KOLUMN = 9
LICZBA_BOMB = 10


# Funkcja odpowiedzialna za załadowanie obrazków używanych w grze.
# Grafiki wykorzystywane w widżetach tkinter muszą istnieć tak długo, jak długo istnieją widżety.
# Nie można grafik wczytywać do zmiennej lokalnej, należy je wczytać do zmiennej globalnej lub pola obiektu widżetu.
def wczytaj_obrazki():
    obrazki = {}
    sciezka = os.path.dirname(os.path.realpath(__file__))  # Dzięki funkcjom z os.path program powinien działać w rożnych systemach operacyjnych

    try:
        for i in range(1, 5):
            obrazki["buzia_"+str(i)] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", f"buzia_{i}.png"))

        for i in range(1, 9):
            obrazki[str(i)] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", f"{i}.png"))

        for i in range(10):
            obrazki["cyfra_"+str(i)+"-a"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", f"cyfra_{i}-a.png"))
            obrazki["cyfra_"+str(i)+"-b"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", f"cyfra_{i}-b.png"))
        obrazki["znak_minus-a"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "znak_minus-a.png"))
        obrazki["litera_O-a"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "litera_O-a.png"))
        obrazki["litera_L-a"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "litera_L-a.png"))
        obrazki["znak_minus-a"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "znak_minus-a.png"))

        obrazki["bomba"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "bomba.png"))
        obrazki["bomba_trafiona"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "bomba_trafiona.png"))
        obrazki["bomba_skreslona"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "bomba_skreslona.png"))
        obrazki["flaga"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "flaga.png"))
        obrazki["pytajnik"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "pytajnik.png"))
        obrazki["pusty"] = tk.PhotoImage(file=os.path.join(sciezka, "grafika", "pusty.png"))
    except tk.TclError:
        sys.exit("Nie można wczytać obrazków!")

    return obrazki


# Utworzenie głównego okna programu
def inicjalizacja_okna():
    root = tk.Tk()
    root.title("Saper")
    root.resizable(False, False)

    return root


# Utworzenie górnej ramki z licznikiem bomb, licznikiem czasu i przyciskiem reset.
# Font użyty do stworzenia grafik dla liczników to: 16 Segments
def inicjalizacja_panelu():
    ramka = tk.Frame(root, relief=tk.SUNKEN, borderwidth=4)
    ramka.pack(fill=tk.X, padx=10, pady=10)

    # Konwertuj liczbę bomb do typu string i wypełnij wiodącymi zerami
    bomby_str = str(ile_bomb).zfill(3)

    bomby = [
        tk.Label(ramka, image=obrazki["cyfra_"+bomby_str[0]+"-a"], bd=0),
        tk.Label(ramka, image=obrazki["cyfra_"+bomby_str[1]+"-a"], bd=0),
        tk.Label(ramka, image=obrazki["cyfra_"+bomby_str[2]+"-a"], bd=0)
    ]

    przycisk = tk.Button(ramka, image=obrazki["buzia_1"], borderwidth=2, command=resetuj_gre)

    czas = [
        tk.Label(ramka, image=obrazki["cyfra_0-b"], bd=0),
        tk.Label(ramka, image=obrazki["cyfra_0-b"], bd=0),
        tk.Label(ramka, image=obrazki["cyfra_0-b"], bd=0)
    ]

    # Kolumna o indeksie 3 powinna zajmować całą dostępną przestrzeń
    ramka.columnconfigure(3, weight=1)

    bomby[0].grid(row=0, column=0, padx=(5, 0))
    bomby[1].grid(row=0, column=1)
    bomby[2].grid(row=0, column=2)

    przycisk.grid(row=0, column=3, pady=5)

    czas[0].grid(row=0, column=4)
    czas[1].grid(row=0, column=5)
    czas[2].grid(row=0, column=6, padx=(0, 5))

    return bomby, czas, przycisk


# Utworzenie dolnej ramki z planszą gry
def inicjalizacja_planszy():
    dolna_ramka = tk.Frame(root, relief=tk.SUNKEN, bd=4)
    dolna_ramka.pack(expand=True, padx=10, pady=(0, 10))

    # Utworzenie planszy z elementami typu Label w roli przycisków
    plansza = [[tk.Label(dolna_ramka, relief=tk.RAISED, image=obrazki["pusty"], bd=1) for i in range(LICZBA_KOLUMN)] for j in range(LICZBA_WIERSZY)]

    for i in range(LICZBA_WIERSZY):
        for j in range(LICZBA_KOLUMN):
            # Własne pola w obiekcie typu tkinter.Label
            plansza[i][j].bomba = False  # Czy dane pole skrywa bombę
            plansza[i][j].wcisniety = False  # Czy kliknięto pole LPM
            plansza[i][j].oznaczony = 0  # Czy kliknięto pole PPM (3 poziomy): 0 - brak oznaczenia, 1 - flaga, 2 - pytajnik
            plansza[i][j].pozycja = {"x":j, "y":i}  # Współrzędne danego pola
            plansza[i][j].ile_bomb_dookola = None  # Informacja o ilości bomb wokół danego pola (początkowo None)

            przypnij_zdarzenia(plansza[i][j])
            plansza[i][j].grid(row=i, column=j)

    return plansza


# Funkcja wyświetlająca liczbę bomb pozostałą do oznaczenia flagą
def ustaw_licznik_bomb(bomby):
    wartosc = str(bomby).zfill(3)  # Poprzedź zerami do 3 miejsc

    if bomby >= 0:
        licznik_bomb[0].config(image=obrazki["cyfra_"+wartosc[0]+"-a"])
    else:
        licznik_bomb[0].config(image=obrazki["znak_minus-a"])

    if bomby >= -99:
        licznik_bomb[1].config(image=obrazki["cyfra_"+ wartosc[1]+"-a"])
        licznik_bomb[2].config(image=obrazki["cyfra_"+ wartosc[2]+"-a"])
    else:
        licznik_bomb[1].config(image=obrazki["litera_O-a"])
        licznik_bomb[2].config(image=obrazki["litera_L-a"])


# Funkcja wyświetlająca czas na liczniku
def ustaw_licznik_czasu(czas):
    wartosc = str(czas).zfill(3)  # Poprzedź zerami do 3 miejsc

    if czas < 999:
        licznik_czasu[0].config(image=obrazki["cyfra_"+wartosc[0]+"-b"])
        licznik_czasu[1].config(image=obrazki["cyfra_"+wartosc[1]+"-b"])
        licznik_czasu[2].config(image=obrazki["cyfra_"+wartosc[2]+"-b"])


# Funkcja odmierzająca czas jaki upłynął od pierwszego kliknięcia LPM lub PPM na planszy.
# Parametr stop=True zatrzymuje odmierzanie czasu. Maksymalny czas gry to 999 [s].
def stoper(stop=False):
    global czas, stoper_id

    if stop == True:
        if stoper_id is not None:
            root.after_cancel(stoper_id)  # Anulowanie kolejnego, oczekującego wywołania metody after
            stoper_id = None
    else:
        czas += 1
        ustaw_licznik_czasu(czas)

        if czas < 999:
            stoper_id = root.after(1000, stoper)  # Wywołaj funkcję stoper po upływie 1000 [ms]
        else:
            for wiersz in plansza:
                for przycisk in wiersz:
                    usun_zdarzenia(przycisk)
            messagebox.showinfo(title="Informacja", message="Koniec gry.\nCzas minął.")


# Funkcja przywracająca początkowe ustawienia gry i obiektów
def resetuj_gre():
    global ile_bomb, czas

    stoper(stop=True)
    czas = -1
    ile_bomb = LICZBA_BOMB

    ustaw_licznik_bomb(ile_bomb)
    ustaw_licznik_czasu(0)
    przycisk_reset.config(image=obrazki["buzia_1"])

    for wiersz in plansza:
        for przycisk in wiersz:
            przycisk.bomba = False
            przycisk.wcisniety = False
            przycisk.oznaczony = 0
            przycisk.config(image=obrazki["pusty"])
            przycisk.config(relief=tk.RAISED)
            przypnij_zdarzenia(przycisk)

    losuj_bomby()


# Sprawdź, czy nastąpił koniec gry zakończony zwycięstwem
def sprawdz_zwyciestwo():
    ile_oznaczonych = 0
    ile_wcisnietych = 0

    # Zlicz pola wciśnięte oraz prawidłowo oznaczone flagą
    for wiersz in plansza:
        for przycisk in wiersz:
            if przycisk.wcisniety == True:
                ile_wcisnietych += 1
            else:
                if przycisk.oznaczony == 1 and przycisk.bomba == True:
                    ile_oznaczonych += 1

    # Warunek zwycięskiego zakończenia gry
    if ile_oznaczonych == LICZBA_BOMB and ile_wcisnietych == LICZBA_WIERSZY * LICZBA_KOLUMN - LICZBA_BOMB:
        stoper(stop=True)
        przycisk_reset.config(image=obrazki["buzia_3"])

        for wiersz in plansza:
            for przycisk in wiersz:
                if przycisk.oznaczony == 1:  # Dla pól oznaczonych flagą usuń zdarzenia
                    usun_zdarzenia(przycisk)

        messagebox.showinfo(title="informacja", message=f"Zwycięstwo!\n\nCzas: {czas}s")


# Rekurencyjnie odsłoń puste pola po kliknięciu LPM w miejscu, gdzie nie ma bomby oraz liczba bomb dookoła wynosi 0
def odslon_puste_pola(poz_x, poz_y):
    # Sprawdź tylko 8 pól wokół centralnego pola o współrzędnych poz_x, poz_y
    for i in range(-1, 2):
        for j in range(-1, 2):
            wiersz = poz_y + i
            kolumna = poz_x + j

            if not (wiersz == poz_y and kolumna == poz_x):  # Nie sprawdzaj dla centralnego pola
                if wiersz >= 0 and wiersz < LICZBA_WIERSZY and kolumna >= 0 and kolumna < LICZBA_KOLUMN:  # Wiersz i kolumna nie mogą wykraczać poza planszę
                    przycisk = plansza[wiersz][kolumna]

                    if przycisk.wcisniety == False and przycisk.oznaczony != 1:  # Jeśli pole nie jest wciśnięte i nie jest oznaczone flagą, to...
                        przycisk.wcisniety = True
                        przycisk.config(relief=tk.SUNKEN)
                        usun_zdarzenia(przycisk)

                        if przycisk.ile_bomb_dookola != 0:  # Jeśli wokół są bomby...
                            przycisk["image"] = obrazki[f"{przycisk.ile_bomb_dookola}"]
                        else:
                            if przycisk.oznaczony == 2:  # Jeśli pole jest oznaczone znakiem zapytania...
                                przycisk["image"] = obrazki["pusty"]
                            odslon_puste_pola(kolumna, wiersz)


# Funkcja zliczająca bomby wokół pola o współrzędnych podanych jako argumenty funkcji
def policz_sasiednie_bomby(poz_x, poz_y):
    licznik = 0

    for i in range(-1, 2):
        for j in range(-1, 2):
            wiersz = poz_y + i
            kolumna = poz_x + j

            # Nie uwzględniamy centralnego elementu w siatce 3x3, dla którego wywoływana jest funkcja
            if not (wiersz == poz_y and kolumna == poz_x):
                # Indeksy x, y dwuwymiarowej tablicy muszą się mieścić w dopuszczalnym zakresie
                if wiersz >= 0 and wiersz < LICZBA_WIERSZY and kolumna >= 0 and kolumna < LICZBA_KOLUMN:
                    if plansza[wiersz][kolumna].bomba == True:
                        licznik += 1

    return licznik


# Funkcja przypisująca bomby losowym polom planszy
def losuj_bomby():
    losy = random.sample(range(LICZBA_WIERSZY*LICZBA_KOLUMN), LICZBA_BOMB)
    losy.sort()

    for liczba in losy:
        i = liczba // LICZBA_KOLUMN
        j = liczba % LICZBA_KOLUMN
        plansza[i][j].bomba = True

    # Policz dla każdego pola planszy, ile bomb jest na sąsiednich polach
    for w in range(LICZBA_WIERSZY):
        for k in range(LICZBA_KOLUMN):
            plansza[w][k].ile_bomb_dookola = policz_sasiednie_bomby(k, w)


def przypnij_zdarzenia(obiekt):
    obiekt.bind("<ButtonRelease-1>", lewy_klik)
    obiekt.bind("<ButtonRelease-3>", prawy_klik)
    obiekt.bind("<ButtonPress-1>", buzia)
    obiekt.bind("<ButtonPress-3>", buzia)


def usun_zdarzenia(obiekt):
    obiekt.unbind("<ButtonRelease-1>")
    obiekt.unbind("<ButtonRelease-3>")
    obiekt.unbind("<ButtonPress-1>")
    obiekt.unbind("<ButtonPress-3>")


# Funkcja przypisana do zdarzeń ButtonPress-1 i ButtonPress-3
def buzia(event):
    przycisk_reset["image"] = obrazki["buzia_2"]


# Funkcja przypisana do zdarzenia ButtonRelease-1
def lewy_klik(event):
    klikniety_przycisk = event.widget  # Pobierz referencję do obiektu, który wywołał zdarzenie
    przycisk_reset["image"] = obrazki["buzia_1"]

    if klikniety_przycisk.oznaczony != 1:  # Dalsze działania dotyczą pól, które nie są oznaczone flagą
        global stoper_id
        if stoper_id is None:  # Uruchom odliczanie czasu, jeśli to jeszcze nie nastąpiło
            stoper()

        if klikniety_przycisk.wcisniety == False:
            klikniety_przycisk.wcisniety = True
            klikniety_przycisk.config(relief=tk.SUNKEN)

        # Kliknięcie przycisku z bombą oznacza koniec gry
        if klikniety_przycisk.bomba == True:
            klikniety_przycisk["image"] = obrazki["bomba_trafiona"]
            przycisk_reset["image"] = obrazki["buzia_4"]

            # Wyszukaj i wyświetl wszystkie pozostałe bomby
            for wiersz in plansza:
                for przycisk in wiersz:
                    if przycisk is not klikniety_przycisk:
                        if przycisk.oznaczony == 1:  # Jeśli pole oznaczone jest flagą...
                            if przycisk.bomba == False:  # Jeśli na danym polu nie ma bomby...
                                przycisk["image"] = obrazki["bomba_skreslona"]
                                przycisk.wcisniety = True
                                przycisk["relief"] = tk.SUNKEN
                        else:  # Jeśli pole nie jest oznaczone flagą
                            if przycisk.bomba == True:  # Jeśli na danym polu jest bomba...
                                przycisk["image"] = obrazki["bomba"]
                                przycisk.wcisniety = True
                                przycisk["relief"] = tk.SUNKEN

                    usun_zdarzenia(przycisk)  # Usuń zdarzenia dla wszystkich pól planszy

            stoper(stop=True)  # Zatrzymaj odmierzanie czasu
            messagebox.showinfo(title="Informacja", message="Porażka!\nSpróbuj ponownie.")
        else:  # Jeśli na danym polu nie ma bomby...
            usun_zdarzenia(klikniety_przycisk)

            if klikniety_przycisk.ile_bomb_dookola != 0:  # Jeśli dookoła są jakieś bomby...
                klikniety_przycisk["image"] = obrazki[f"{klikniety_przycisk.ile_bomb_dookola}"]
            else:  # Jeśli dookoła nie ma bomb...
                if klikniety_przycisk.oznaczony == 2:  # Jeśli pole oznaczone jest znakiem zapytania...
                    klikniety_przycisk["image"] = obrazki["pusty"]
                odslon_puste_pola(klikniety_przycisk.pozycja["x"], klikniety_przycisk.pozycja["y"])

            # Sprawdź, czy oznaczono flagą wszystkie bomby oraz odsłonięto pozostałe pola
            sprawdz_zwyciestwo()


# Funkcja przypisana do zdarzenia ButtonRelease-3
def prawy_klik(event):
    global ile_bomb, stoper_id

    if stoper_id is None:  # Uruchom odliczanie czasu, jeśli to jeszcze nie nastąpiło
        stoper()

    klikniety_przycisk = event.widget  # Pobierz referencję do obiektu, który wywołał zdarzenie
    przycisk_reset["image"] = obrazki["buzia_1"]

    if klikniety_przycisk.oznaczony == 1:  # Jeśli pole oznaczone jest flagą, to oznacz je znakiem zapytania
        klikniety_przycisk.oznaczony = 2
        klikniety_przycisk["image"] = obrazki["pytajnik"]
        ile_bomb += 1
    elif klikniety_przycisk.oznaczony == 2:  # Jeśli pole oznaczone jest znakiem zapytania, to ustaw brak oznaczeń
        klikniety_przycisk.oznaczony = 0
        klikniety_przycisk["image"] = obrazki["pusty"]
    else:  # Jeśli pole nie jest oznaczone, to oznacz je flagą
        klikniety_przycisk.oznaczony = 1
        klikniety_przycisk["image"] = obrazki["flaga"]
        ile_bomb -= 1

    ustaw_licznik_bomb(ile_bomb)

    # Sprawdź, czy oznaczono flagą wszystkie bomby oraz odsłonięto pozostałe pola
    sprawdz_zwyciestwo()


# Główma funkcja programu
def main():
    global root, plansza, obrazki
    global ile_bomb, czas, stoper_id
    global licznik_bomb, licznik_czasu, przycisk_reset

    # Parametry początkowe
    czas = -1
    stoper_id = None
    ile_bomb = LICZBA_BOMB

    if (LICZBA_BOMB > LICZBA_WIERSZY * LICZBA_KOLUMN):
        sys.exit("LICZBA_BOMB nie może być większa od rozmiaru planszy!")

    # Inicjalizacja elementów graficznych programu
    root = inicjalizacja_okna()
    obrazki = wczytaj_obrazki()
    licznik_bomb, licznik_czasu, przycisk_reset = inicjalizacja_panelu()
    plansza = inicjalizacja_planszy()

    losuj_bomby()

    root.mainloop()


# Wywołanie funkcji main i uruchomienie gry
if __name__ == "__main__":
    main()
