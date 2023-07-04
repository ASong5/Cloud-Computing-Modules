#!/usr/bin/python3

# Andrew Song - 1204822
# Assignment 2
# CIS4010
# 02/11/23

from tabulate import tabulate
import pandas as pd
from ddb_modules import *


def generate_report_A(ddb, country_name, user_name):
    try:
        country_data = query_item(
            ddb, f"{user_name}_countries", "CountryName", country_name)["Item"]
        area_data = sorted(query_item(ddb, f"{user_name}_countries", None, None, None, None, "CountryName,Area")[
                           "Items"], key=lambda x: x["Area"], reverse=True)
        country_pop_data = query_item(
            ddb, f"{user_name}_population", "CountryName", country_name)["Item"]
        population_data = query_item(ddb, f"{user_name}_population")["Items"]

        area_rank = 0
        i = 0
        for item in area_data:
            if item["CountryName"] == country_name:
                area_rank = i + 1
                break
            i += 1

        pop_ranks = {}
        pop_density_ranks = {}
        area_map = {}
        for area_dict in area_data:
            area_map[area_dict["CountryName"]] = area_dict["Area"]

        for year in country_pop_data.keys():
            if not year.isdigit():
                continue
            given_country_pop = country_pop_data[year]
            given_country_area = area_map.get(country_name, None)
            population_list = []
            pop_density_list = []
            for country_dict in population_data:
                country_pop = country_dict.get(year, None)
                country_area = area_map.get(country_dict["CountryName"], None)
                if country_pop is not None and country_area is not None:
                    population_list.append(country_pop)
                    pop_density_list.append(country_pop / country_area)
            if given_country_pop is None or given_country_pop not in population_list or not population_list:
                pop_rank = None
                pop_density_rank = None
            else:
                population_list.sort(reverse=True)
                pop_rank = population_list.index(given_country_pop) + 1
                pop_density_rank = len([x for x in pop_density_list if x > (given_country_pop / given_country_area)]) + 1
            pop_ranks[year] = pop_rank
            pop_density_ranks[year] = pop_density_rank

        if len(country_data):
            with open(f"Report A - {country_data['CountryName']}.txt", "w", encoding="utf-8-sig") as f:
                f.write(f"{country_data['CountryName']}\n")
                f.write(F"[Official Name: {country_data['OfficialName']}]\n")
                f.write(tabulate(pd.DataFrame([f"Area: {area_map.get(country_name, None)} sq km ({area_rank})",
                      f"Official/National Languages: {country_data['Languages']}\nCapital City: {country_data['Capital']}"]), tablefmt="grid", showindex=False))
                f.write("\n\nPopulation\n")

                table_data = {'Year': [], 'Population': [], 'Population Rank': [
                ], 'Population Density': [], 'Population Density Rank': []}

                for year in pop_ranks.keys():
                    pop = country_pop_data.get(year, None)
                    pop_rank = pop_ranks[year]
                    density_rank = pop_density_ranks[year]
                    if pop is not None:
                        density = pop / area_map.get(country_name, None)
                    else:
                        density = None
                    table_data['Year'].append(year)
                    table_data['Population'].append(pop)
                    table_data['Population Rank'].append(pop_rank)
                    table_data['Population Density'].append(density)
                    table_data['Population Density Rank'].append(density_rank)

                df = pd.DataFrame(table_data).sort_values(by=["Year"])
                df['Population'] = df['Population'].apply(
                    lambda x: f'{int(x):,}' if pd.notnull(x) else '')
                df['Population Density'] = df['Population Density'].apply(
                    lambda x: f'{x:.2f}' if pd.notnull(x) else '')
                df = df.dropna(how="any")
                if df.iloc[0].isna().any():
                    df = df.iloc[1:]
                if df.iloc[-1].isna().any():
                    df = df.iloc[:-1]
                f.write(tabulate(df, headers='keys',
                      tablefmt="grid", showindex=False))
        return True
    except Exception as err:
        return False


def generate_report_B(ddb, year, user_name):
    try:
        countries_data = query_item(
            ddb, f"{user_name}_countries", None, None, None, None, "CountryName")["Items"]
        population_data = query_item(ddb, f"{user_name}_population")["Items"]
        gdp_data = query_item(ddb, f"{user_name}_gdp")["Items"]
        year_pop = []
        for item in population_data:
            if year in item:
                year_pop.append(
                    {"Country Name": item["CountryName"], "Population": item[year]})
        pop_df = pd.DataFrame(year_pop).sort_values(
            "Population", ascending=False)
        pop_df["Rank"] = pop_df["Population"].rank(
            ascending=False, method="dense")
        pop_df['Population'] = pop_df['Population'].apply(
            lambda x: f'{int(x):,}' if pd.notnull(x) else '')
        pop_df = pop_df.dropna(how="any")
        if pop_df.iloc[0].isna().any():
            pop_df = pop_df.iloc[1:]
        if pop_df.iloc[-1].isna().any():
            pop_df = pop_df.iloc[:-1]

        area_data = query_item(
            ddb, f"{user_name}_countries", None, None, None, None, "CountryName,Area")["Items"]
        year_area = []
        for item in area_data:
            year_area.append(
                {"Country Name": item["CountryName"], "Area": item["Area"]})
        area_df = pd.DataFrame(year_area).sort_values("Area", ascending=False)
        area_df["Rank"] = area_df["Area"].rank(ascending=False, method="dense")
        area_df['Area'] = area_df['Area'].apply(
            lambda x: f'{int(x):,}' if pd.notnull(x) else '')
        area_df = area_df.dropna(how="any")
        if area_df.iloc[0].isna().any():
            area_df = area_df.iloc[1:]
        if area_df.iloc[-1].isna().any():
            area_df = area_df.iloc[:-1]

        pop_density_df = pd.merge(
            pop_df, area_df, on="Country Name").dropna(how="any")
        pop_density_df["Density (people / sq km)"] = pop_density_df["Population"].str.replace(
            ",", "").astype(float) / pop_density_df["Area"].str.replace(",", "").astype(float)
        pop_density_df = pop_density_df[[
            "Country Name", "Density (people / sq km)"]].sort_values("Density (people / sq km)", ascending=False)
        pop_density_df["Rank"] = pop_density_df["Density (people / sq km)"].rank(
            ascending=False, method="dense")
        pop_density_df["Density (people / sq km)"] = pop_density_df["Density (people / sq km)"].apply(
            lambda x: '{:,.2f}'.format(x))
        pop_density_df = pop_density_df.dropna(how="any")
        if pop_density_df.iloc[0].isna().any():
            pop_density_df = pop_density_df.iloc[1:]
        if pop_density_df.iloc[-1].isna().any():
            pop_density_df = pop_density_df.iloc[:-1]

        for data in gdp_data:
            data.pop("Currency", None)

        df_gdp = pd.DataFrame(gdp_data).sort_values("CountryName")

        min_year = int(min([col for col in df_gdp.columns if col.isnumeric()]))
        max_year = int(max([col for col in df_gdp.columns if col.isnumeric()]))

        decades = list(range(min_year // 10 * 10, max_year + 10, 10))

        with open(f"Report B - {year}.txt", "w", encoding="utf-8-sig") as f:
            f.write("Global Report\n")
            f.write(f"Year: {year}\n")
            f.write(f"Number of Countries: {len(countries_data)}\n")

            f.write("\nTable of Countries Ranked by Population (largest to smallest)\n")
            f.write(tabulate(pop_df, headers="keys",
                  tablefmt="grid", showindex=False))
            f.write("\n\n")
            f.write("Table of Countries Ranked by Area (largest to smallest)\n")
            f.write(tabulate(area_df, headers="keys",
                  tablefmt="grid", showindex=False))
            f.write("\n\n")
            f.write("Table of Countries Ranked by Density (largest to smallest)\n")
            f.write(tabulate(pop_density_df, headers="keys",
                  tablefmt="grid", showindex=False))
            f.write("\n\n")
            f.write("GDP Per Capita for all Countries\n")
            for i in range(len(decades)-1):
                df_decade = df_gdp[['CountryName'] + [str(year) for year in range(
                    decades[i], decades[i+1])]].rename(columns={"CountryName": "Country Name"})
                f.write(f"{decades[i]}'s Table\n")
                f.write(tabulate(df_decade, headers='keys',
                      tablefmt="grid", showindex=False))
                f.write("\n\n")
        return True
    except Exception as err:
        return False
