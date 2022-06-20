# **Program do automatycznej analizy giełdowej.**
Program został utworzony w celach edukacyjnych.
W ramach realizacji projektu wykorzystano bibliotekę, która umożliwia testowanie swoich
algorytmów oraz strategii działań na rynku poprzez tzw. konta demonstracyjne. Posiadają one
określony budżet w wysokości 100,000$, który można dowolnie resetować na ich stronie Alpaca
Markets. Pozwoli to na sprawdzenie nowych strategii, bez utraty rzeczywistego budżetu.
Generowany wykres wyszukanej wcześniej przez użytkownika spółki będzie zawierał domyślnie
dane dotyczące historycznych cen ich akcji oraz pod wykresami będzie informacja o ostatniej znanej
cenie papieru wartościowego. Każdy użytkownik będzie miał dodatkowo możliwość generacji na
wykresie wskaźników takich jak : RSI, MACD, MFI, EMA. Natomiast użytkownicy uprzywilejowani
otrzymają możliwość generacji predykcji dotyczących cen akcji spółki.

### **Wymagania**

Do poprawnego działania programu należy pobrać pakiety zawarte w pliku requirements.txt oraz system zarządzania bazą danych PostgreSQL.

### **Instalacja**

W celu poprawnego działania programu w pliku _config.py_ wewnątrz katalogu _Database_ należy zadeklarować wartości zmiennych dotyczących połączenia z bazą danych.

Kolejnym etapem jest deklaracja wartości zmiennych zawartych w pliku _config.py_ wewnątrz katalogu _Stock_.
zmienne te należy zadeklarować zgodnie z dokumentacją biblioteki https://github.com/alpacahq/alpaca-trade-api-python.
W celu uzyskania klucza identyfikującego oraz sekretnego klucz konta w Alpaca Markets, należy utworzyć konto (https://app.alpaca.markets/signup) oraz uzyskać klucz do konta w zakładce Paper Trading.

Po rejestracji pierwszego użytkownika, należy manualnie ustawić jego poziom uprawnień w bazie danych na wartość 2 (co identyfikuje poziom uprawnień administratora).

### **Użytkowanie**

Administrator może przydzielać stopnie uprawnień poszczególnych użytkowników.
W celu umożliwienia korzystania z funkcjonalności kupna oraz sprzedaży papierów wartościowych poszczególnych spółek każdy uprzywilejowany użytkownik powinien podać uprzednio wygenerowany sekretny klucz oraz klucz identyfikujący do API Alpaca Markets (w wersji Paper Trading).