import argparse
from pathlib import Path
import matplotlib.pyplot as plt

from data_loader import (
    download_multiple_gios_archives,
    edit_df,
    download_gios_metadata,
    create_code_map,
    multiindex_code_city,
    correct_datetime_index
)

from average_and_limits import find_above_norm, monthly_mean
from visualizations import plot_average, bar_plots

def main(year, daily_norm, cities, outdir):

    # downloading the data
    outdir = Path(outdir)
    figdir = outdir / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)

    years = [year]

    gios_ids = {2006: '227', 2007: '228', 2008: '229', 2009: '230', 2010: '231', 2011: '232',
                2012: '233', 2013: '234', 2014: '302', 2015: '236', 2016: '602', 2017: '262',
                2018: '603', 2019: '322', 2020: '424', 2021: '486', 2022: '524', 2023: '564', 2024: '582'}
    filenames = {2006: '2006_PM2.5_1g.xlsx', 2007: '2007_PM2.5_1g.xlsx', 2008: '2008_PM2.5_1g.xlsx',
                 2009: '2009_PM2.5_1g.xlsx', 2010: '2010_PM2.5_1g.xlsx', 2011: '2011_PM2.5_1g.xlsx',
                 2012: '2012_PM2.5_1g.xlsx', 2013: '2013_PM2.5_1g.xlsx', 2014: '2014_PM2.5_1g.xlsx',
                 2015: '2015_PM25_1g.xlsx', 2016: '2016_PM25_1g.xlsx', 2017: '2017_PM25_1g.xlsx',
                 2018: '2018_PM25_1g.xlsx', 2019: '2019_PM25_1g.xlsx', 2020: '2020_PM25_1g.xlsx',
                 2021: '2021_PM25_1g.xlsx', 2022: '2022_PM25_1g.xlsx', 2023: '2023_PM25_1g.xlsx',
                 2024: '2024_PM25_1g.xlsx'}
    
    if year not in gios_ids:
        print(f"Brak danych dla roku {year} - pomijam przetwarzanie.")
        return

    raw = download_multiple_gios_archives(years, gios_ids, filenames)
    cleaned = edit_df(raw)

    metadata = download_gios_metadata("https://powietrze.gios.gov.pl/pjp/archives/downloadFile/622")
    mapped = create_code_map(metadata, cleaned)
    mapped = multiindex_code_city(mapped, metadata)
    mapped = correct_datetime_index(mapped)
    
    # we have only one year, so no merging of the years
    df = list(mapped.values())[0]

    # calculating exceedance days
    norms = find_above_norm(
        df,
        years=[year],
        sort_by=year,
        norm=daily_norm
    )

    norms.to_csv(outdir / "exceedance_days.csv")

    # plotting bar plots for exceedance days
    bar_plots(
        norms,
        year=year,
        show=False
    )
    plt.savefig(figdir / "exceedance_days.png", dpi=150)
    plt.close()

    # calulating monthly means
    monthly = monthly_mean(df)
    monthly.to_csv(outdir / "monthly_means.csv", index=True)

    monthly_city = monthly.T.groupby(level=0).mean().T

    # plotting average monthly PM2.5
    plot_average(
        monthly_df_grouped=monthly_city,
        years=[year],
        cities=cities,
        show=False
    )
    plt.savefig(figdir / "monthly_trends.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--daily_norm", type=float, required=True)
    parser.add_argument("--cities", nargs="+", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    main(args.year, args.daily_norm, args.cities, args.outdir)
