# Zadanie 4 ZTP
### Agnieszka Prudło
Repozytuorium zawiera rozwiązania do zadania 4 z ZTP. 


## Uruchomienie programu

W pliku config/task4.yaml użytkownik ustawia lata, np.:

years: [2021, 2024]

Następnie wpisuje w terminalu:

snakemake -s Snakefile_task4 --cores 1

lub:

snakemake -s Snakefile_task4 --cores 1 --rerun-triggers checksum

To pierwsze wywyołanie jest domyśne - Snakemake sprawdza, czy pliki wynikowe są aktualne na podstawie czasu modyfikacji (mtime). Można wymusić ponowne policzenie plików wynikowych tylko wtedy, gdy zawartość wejść się zmieniła, używając flagi --rerun-triggers checksum. Dzięki temu pipeline reaguje na zmiany danych nawet jeśli ich timestamp się nie zmienił.

## Scenariusz działania

1) Użytkownik ustawia:

- years: [2021, 2024]

Uruchamia:

- snakemake -s Snakefile_task4 --cores 1

Pipeline:

- uruchamia kod running_pm25.py dla lat 2021 i 2024
- uruchamia kod pubmed_fetch.py dla lat 2021 i 2024
- uruchamia kod generate_report.py i generuje raport dla {2021, 2024}

2) Użytkownik zmienia config na:

- years: [2019, 2024]

Uruchamia:

- snakemake -s Snakefile_task4 --cores 1

Pipeline:
- uruchamia kod running_pm25.py dla roku 2019; 2024 zostaje pominięty
- uruchamia kod pubmed_fetch.py dla roku 2019; 2024 zostaje pominięty
- uruchamia kod generate_report.py i generuje raport dla {2019, 2024}

## Weryfikacja tego, że pliki nie przeliczają się drugi raz

Przy uruchomieniu linijki:

snakemake -s Snakefile_task4 --cores 1 --summary


Pojawia się informacja, którep pliki są aktualne, a które muszą zostać przeliczone od nowa.

Po uruchomieniu programu wyświetla się również informacja typu:

Job stats:
job             count
`------------  -------`
all                 1
pm25_metrics        2
pubmed_fetch        2
report              1
total               6

Widać tutaj, że pm25_metrics i pubmed_fetch uruchamiają sie dla dwóch lat. Jeśli nie byłoby potrzeby uruchomienia ich dla któregoś roku informacja ta wyglądałaby tak:

Job stats:
job             count
`------------  -------`
all                 1
pm25_metrics        1
pubmed_fetch        1
report              1
total               4

Jeśli wszystkie pliki są aktualne, po uruchomieniu programu dostajemy informację:

""Nothing to be done (all requested files are present and up to date).""

## Zawartość repozytorium


Folder config zawiera plik task4.yaml. Są tam parametry do podania przez użytkownika. Jest to jedyny plik do edytowania przez użytkownika.

Folder src zawiera kody źródłowe podzielone na 3 części: literature, pm25 i report.

-Folder pm25 zawiera pliki powstałe dla zadań 1 i 3 (average_and_limits.py, data_loader.py i visualizations.py) oraz running_om25.py zawierający kod, który używa funkcji z reszty plików w sposób potrzebny do odecnego zadania.

-Folder literature zawiera plik pubmed_fetch.py pobierający dane z bazy danych PubMed.

-Folder report zawiera plik generate_report.py tworzący raport MarkDown z danych uzyskanych w tym zadaniu.

Folder tests zawiera plik test_pubmed_fetch.py zawierający testy pliku pubmed_fetch.py.

Plik Snakefile_task4 uruchamia pipline za pomocą Snakemake.