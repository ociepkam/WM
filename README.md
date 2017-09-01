# Test pamieci roboczej

1) Wartości parametrów w pliku xlsx wygenerowanym przez general_experiment.py:
    
    Każdy wiersz oznacza trial, który zostanie wyświetlony na ekranie
    
    A) BLOCK_NUMBER
    - liczba naturalna dodatnia, która określa do którego bloku należy dany trial
    - bloki zostaną wyświetlone kolejno od najniższego numeru do najwyższego
    - triale należące do tego samego bloku nie muszą się znajdować bezpośrednio po sobą
    - kolejność występowania triali w bloku określa kolejność wyświetlenia ich podczas eksperymentu (chyba, że zostanie włączona opcja randomizacji)
    
    B) TRIAL_TYPE
    - może przyjmować nastepujące wartości
        * instruction (zawiera tylko i wyłącznie informacje w kolumnie A, B, R, S)
        * training
        * experiment
    
    C) ELEMENTS
     - liczba naturalna dodatnia z przedziału 1-25
     - określa ile figur znajduje sie w danej macierzy - trialu
     
    D) FEEDB
    - może przyjmować wartości 0, 1 albo 2
        * 0 (nie wyświetlaj informacji o poprawności rozwiązania tego triala)
        * 1 (wyświetl informację o poprawności rozwiązania tego triala)
        * 2 (na koniec testu podaj całkowity wynik wszystkich rozwiązanych triali)
        
    E) FIGURE
    - może przyjąć wartość 0, 1 albo -1
        * 0 (podczas zmieny cech (CHANGE = 2) nie bierz pod uwagę kształtu figury)
        * 1 (podczas zmieny cech (CHANGE = 2) bierz pod uwagę kształt figury)
        * -1 (procedura działa na literach greckich)
        
    F) COLOR
    - może przyjąć wartość 0, 1 albo -1
        * 0 (podczas zmieny cech (CHANGE = 2) nie bierz pod uwagę koloru figury)
        * 1 (podczas zmieny cech (CHANGE = 2) bierz pod uwagę kolor figury)
        * -1 (procedura działa na literach greckich)
        
    G) CHANGE
    - może przyjmować wartości 0, 1 albo 2
        * 0 (druga macierz w tralu jest identyczna jak pierwsza)
        * 1 (w macierzy drugiej dwie figury sa zamienione miejscami)
        * 2 (jedna cecha w jednej figurze w macierzy drugiej zostaje zmieniona na inną)
        
    H) UNIQUE
    - może przyjąć wartość 0 albo 1
        * 0 (w macierzy figury mogą się powtarzać)
        * 1 (w macierzy figury się nie powtarzają)
        
    I) ALL
     - może przyjąć wartość 0 albo 1
        * 0 (w macierzy występują tylko pierwsze pięć wartości z każdej cechy)
        * 1 (w macierzy mogą występować wszytkie możliwe kombinacje cech figur)
        
    J) VAR
    - informuje o sposobie wyświetlania wskazówki
    - może przyjmować następujące wartości:
        * ICO (wskazówka pojawia się na początku wyświetlania maski po zniknięciu pierwszej macierzy)
        * FRA (wskazówka pojawia się pod koniec wyświetlania maski po zniknięciu pierwszej macierzy)
        * ROB ((wskazówka pojawia się podczas wyświetlania drugiej macierzy)
        
    K) WAIT
    - liczba naturalna
        * 0 ( po trialu wyświetla napis „naciśnij przycisk” i czeka na reakcję badanego- czas na odpoczynek)
        * inne (czas przerwy pomiędzy próbami określony w sekundach)
    
    L) FTIME
    - liczba naturalna
    - czas wyświetlania pierwszej macierzy określony w sekundach
    
    M) MTIME
    - liczba naturalna
    - czas wyświetlania maski określony w sekundach
    
    N) STIME
    - liczba naturalna
    - czas wyświetlania drugiej macierzy określony w sekundach
    
    O) MAXTIME
    - liczba naturalna
    - czas oczekiwania na odpowiedź liczony od momentu wyswietlenia macierzy 2 określony w sekundach
    
    P) SHINT
    - liczba naturalna
    - czas rozpoczęcia wyświetlania hintu określony w sekundach
        * dla VAR = ROB czas liczony on pojawienia się drugiej macierzy
        * dla VAR /= ROB czas liczony od pojawienia sie maski
        
    R) EHINT
    - liczba naturalna
    - czas wyświetlania hintu określony w sekundach
    
    S) TIP
    - nazwa pliku, w którym znajduje się wskazówka/instrukcja
    
    T) TIP_TIME
    - liczba naturalna
    - czas wyświetlania tip określony w sekundach
        * 0 (czekaj na nacisnięcie spacji)
        
2) Wartości parametrów w pliku yaml wygenerowanym przez concrete_experiment.py:

    - informacje w pliku są podawane zgodnie z kolejnością wyświetlania
    - struktura ma postać drzewiastą. Spis elementów poczynając od najbardziej ogólnych:
        * struktura zewnętrzna
            + eeg
                @ może przyjmować wartości 0, 1
                @ okresla, czy eeg jest włączone podczas badania i nalezy wysyłac triggery
            + fnirs
                @ może przyjmować wartości 0, 1
                @ okresla, czy fnirs jest włączone podczas badania i nalezy wysyłac triggery
            + name (nazwa osoby badanej w postaci ID+SEX+AGE)
            + id (id osoby badanej)
            + sex (płeć osoby badanej)
            + age (wiek osoby badanej)
            + list_of_blocks (lista występujących kolejno po sobie bloków)
        * list_of_blocks
            + matrix (pierwsza macierz)
            + matrix_changed (druga macierz)
            + instruction (nazwa pliku z instrukcją/informacja o przerwie)
            + instruction_time ( czas wyświetlania instrukcją/informacja o przerwie; jeżeli -1 czekaj na spację)
            + instruction_type ( tekxt, image)
            + size (maksymalna liczba możliwych elementów w macierzy)
            + pozostałe parametry opisane w punkcie 1 nimniejszego dokumentu
        * matrix / matrix_changed
            + lista długości "size"
            + elementy oznaczają kolejne figury w macierzy
                @ None (w tym miejscu nie bedzie żadnej figury)
                @ inne (figura, która powinna byc wyświetlona na danej pozycji)
                
http://image.online-convert.com/convert-to-svg