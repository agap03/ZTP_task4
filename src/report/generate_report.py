import argparse
import yaml
import pandas as pd
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

# parse command-line arguments
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args()

# Zwraca n najczęstszych słów w liście tytułów
def top_words(titles, n=10):
    stopwords = {"the", "and", "of", "in", "to", "a", "for", "with", "on", "by", "an"}
    words = []

    for t in titles.dropna():
        for w in t.lower().split():
            w = w.strip(".,!?()[]:;\"'")
            if w and w not in stopwords:
                words.append(w)
    return Counter(words).most_common(n)

def main():
    args = parse_args()
    
    # load config
    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    years = cfg["years"]
    cities = cfg['pm25']["cities"]

    out = []

    # HEADER
    out.append("# Task 4 - Raport końcowy\n")
    out.append("Analiza jakości powietrza (PM2.5) oraz literatury naukowej (PubMed).\n")
    out.append(f"**Lata:** {', '.join(map(str, years))}\n")
    out.append(f"**Miasta:** {', '.join(cities)}\n")

    # PM2.5
    out.append("## PM2.5 - podsumowanie\n")
    out.append("Tabela przedstawia liczbę dni z przekroczeniem normy PM2.5.\n")

    out.append(
        "Liczba dni w roku, w których średnie dobowe stężenie PM2.5 "
        "przekroczyło obowiązującą normę.\n"
    )

    # For each year, read the exceedance days and combine
    pm25_cols = []
    for y in years:
        df = pd.read_csv(f"results/pm25/{y}/exceedance_days.csv")
        df = df.groupby("Miejscowość").sum()
        df = df.rename(columns={"exceedance_days": str(y)})
        df = df.drop(columns=["Kod stacji"])
        pm25_cols.append(df)

    result = pd.concat(pm25_cols, axis=1)

    out.append(result.to_markdown(index=True))
    out.append("\n")

    out.append(
        "Średnie miesięczne wartości PM2.5 (uśrednione po wszystkich stacjach).\n"
    )

    # For each year, include exceedance days plot
    for y in years:
        out.append(f"**Liczba dni z przekroczeniem normy PM2.5 dla roku {y} (najwyższe i najniższe wartości):**\n")
        out.append(f"![Dni przekroczeń PM2.5](pm25/{y}/figures/exceedance_days.png)\n")

    # For each year, include monthly means and plots
    for y in years:
        out.append(f"### Rok {y}\n")
        monthly = pd.read_csv(f"results/pm25/{y}/monthly_means.csv", header=[0, 1])
        cols = monthly.columns
        new_cols = [('','') if i==1 else col for i, col in enumerate(cols)]
        monthly.columns = pd.MultiIndex.from_tuples(new_cols)

        out.append(monthly.to_markdown(index=False))
        out.append("\n")

        out.append("**Trend średnich miesięcznych:**\n")
        out.append(f"![Trend PM2.5 {y}](pm25/{y}/figures/monthly_trends.png)\n")


    # LITERATURE
    out.append("## Literatura (PubMed)\n")

    for y in years:
        out.append(f"### Rok {y}\n")

        papers = pd.read_csv(f"results/literature/{y}/pubmed_papers.csv")
        summary = pd.read_csv(f"results/literature/{y}/summary_by_year.csv")
        journals = pd.read_csv(f"results/literature/{y}/top_journals.csv")

        out.append(f"**Liczba publikacji dla zapytania:** {len(papers)}\n")

        out.append("#### Trend liczby publikacji (wg roku publikacji)\n")
        out.append(summary.to_markdown(index=False))
        out.append("\n")

        out.append(f"![Liczba publikacji wg roku](literature/{y}/papers_by_year.png)\n")

        out.append("#### Najczęściej występujące czasopisma\n")
        out.append(journals.to_markdown(index=False))
        out.append("\n")

        out.append("#### Przykładowe tytuły publikacji\n")
        for t in papers["title"].dropna().head(5):
            out.append(f"- {t}")
        out.append("\n")


    # dodatkowa analiza tytułów i wykres porównawczy
    df_compare = []

    for y in years:
        papers_y = pd.read_csv(f"results/literature/{y}/pubmed_papers.csv")
        
        out.append(f"#### Top słowa w tytułach publikacji - {y}\n")
        top = top_words(papers_y["title"], n=10)

        for word, count in top:
            out.append(f"- {word}: {count}")
        out.append("\n")

        df_compare.append(pd.Series(dict(top), name=str(y)))

    # wykres porównawczy dla wszystkich lat
    df_compare = pd.concat(df_compare, axis=1).fillna(0).astype(int)
    df_compare.plot.bar(figsize=(12, 6))
    plt.ylabel("Liczba wystąpień")
    plt.title("Top słowa w tytułach publikacji")
    fig_path = Path("results/literature/top_words.png")
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()

    out.append(f"![Top słowa](literature/top_words.png)\n")

    Path(args.output).write_text("\n".join(out), encoding="utf-8")



if __name__ == "__main__":
    main()
