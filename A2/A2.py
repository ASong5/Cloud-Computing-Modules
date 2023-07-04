#!/usr/bin/python3

# Andrew Song - 1204822
# Assignment 2
# CIS4010
# 02/11/23
import configparser
import sys
import boto3
import os
import pandas as pd
import csv
import time
from tabulate import tabulate
from ddb_modules import *
from report_gen import *

user_name = ""


def init_aws_connection():
    config = configparser.ConfigParser()
    config.read("DDB.conf")
    aws_access_key_id = config['default']['aws_access_key_id']
    aws_secret_access_key = config['default']['aws_secret_access_key']
    aws_region = config['default']['region']

    #
    #  Establish an AWS session
    #
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    global user_name
    user_name = session.client("sts").get_caller_identity()['UserId']
    #
    #  Set up resources
    #

    try:
        ddb = session.resource('dynamodb')
    except:
        print("Could not connect to Dynamo DB")

    return ddb


def parse_csv(csv):
    try:
        data = pd.read_csv(csv)
        return data
    except Exception as err:
        print("Could not parse csv.", err)


def initial_load(ddb):
    try:
        country_data = parse_csv("un_shortlist.csv")
        with open("shortlist_languages.csv", "r", encoding="utf-8-sig") as fr, open("shortlist_languages_bk.csv", "w", encoding="utf-8-sig") as fw:
            reader = csv.reader(fr, delimiter=",")
            writer = csv.writer(fw)
            for row in reader:
                if len(row) > 3:
                    new_language = row[2]
                    for i in range(len(row), 3, -1):
                        new_language += ", " + row[i - 1]
                    writer.writerow([row[0], row[1], new_language])
                else:
                    writer.writerow([row[0], row[1], row[2]])
        os.remove("shortlist_languages.csv")
        os.rename("shortlist_languages_bk.csv", "shortlist_languages.csv")

        language_data = parse_csv("shortlist_languages.csv")
        capitals_data = parse_csv("shortlist_capitals.csv")
        area_data = parse_csv("shortlist_area.csv")
        pop_data = parse_csv("shortlist_curpop.csv")
        gdp_data = parse_csv("shortlist_gdppc.csv")

        countries = pd.merge(
            pd.merge(pd.merge(country_data, language_data), capitals_data), area_data).rename(columns={"Country Name": "CountryName", "Official Name": "OfficialName"})
        population = pop_data.drop(
            labels="Currency", axis=1).rename(columns={"Population 1970": "1970", "Country": "CountryName"})
        gdp = pd.merge(gdp_data, pop_data[["Country", "Currency"]])
        gdp_cols = list(gdp.columns.values)
        gdp_cols.insert(1, gdp_cols[-1])
        gdp_cols.pop()
        gdp = gdp[gdp_cols].rename(columns={"Country": "CountryName"})

        create_table(ddb, f"{user_name}_countries", "CountryName")
        create_table(ddb, f"{user_name}_population", "CountryName")
        create_table(ddb, f"{user_name}_gdp", "CountryName")

        load_records(ddb, f"{user_name}_countries", countries)
        load_records(ddb, f"{user_name}_population", population)
        load_records(ddb, f"{user_name}_gdp", gdp)

        return True

    except Exception as err:
        print("Initial load failed.", err)
        return False


def main():
    try:
        print("Connecting to AWS DynamoDB... Please wait")
        time.sleep(1)
        ddb = init_aws_connection()
        print("Connected to AWS DynamoDB")
    except Exception as err:
        print("Could not connect to AWS DynamoDB.", err)

    try:
        print("Creating tables. Please wait...\n")
        initial_load(ddb)
    except Exception as err:
        print("Could not load initial data into tables", err)

    stopped = False
    print("Welcome to A2 - DynamoDB Modules with Boto3 and Report Generator")
    time.sleep(2)
    try:
        while (not stopped):
            print("\nChoose an action to perform:")
            time.sleep(1)
            print("(1) Generate Report A")
            time.sleep(1)
            print("(2) Generate Report B")
            time.sleep(1)
            print("(3) Add Missing Information to Table")
            time.sleep(1)
            print("(4) To exit the application. Or type 'exit'")
            time.sleep(1)
            while (True):
                option = input("> ")
                match option:
                    case "1":
                        print(
                            "\nEnter the name of the country you would like to generate a report for.")
                        option = input("> ")
                        if (not generate_report_A(ddb, option, user_name)):
                            print("Could not generate report. Please try again")
                            break
                        else:
                            print("Success!")
                            break
                    case "2":
                        print(
                            "\nEnter the year you would like to generate a report for.")
                        option = input("> ")
                        if (not generate_report_B(ddb, option, user_name)):
                            print("Could not generate report. Please try again")
                            break
                        else:
                            print("Success!")
                            break
                    case "3":
                        tables = list_tables(ddb)["TableNames"]
                        print("\nTables:\n")
                        for i in range(1, len(tables) + 1):
                            print(f"({i}) {tables[i - 1]}")
                        print("\nSelect a table by number\n")
                        option = int(input("> "))
                        try:
                            table_name = tables[option - 1]
                            if table_name == f"{user_name}_population" or table_name == f"{user_name}_gdp":
                                print(
                                    "Which country would you like to add missing information for?\n")
                                country = input("> ")
                                print(
                                    "\nWhat year would you like to add or update?\n")
                                year = int(input("> "))
                                if table_name == f"{user_name}_population":
                                    print(
                                        f"\nEnter the population for {country} in {year}:\n")
                                    pop = int(input("> "))
                                    update_item(ddb, table_name, {
                                                year: pop}, "SET", "CountryName", country, None, None)
                                    print("Success!")
                                    break
                                elif table_name == f"{user_name}_gdp":
                                    print(
                                        f"\nEnter the gdp for {country} in {year}:\n")
                                    gdp = int(input("> "))
                                    update_item(ddb, table_name, {
                                                year: gdp}, "SET", "CountryName", country, None, None)
                                    print("Success!")
                                    break
                            else:
                                print(
                                    "Which country would you like to add missing information for?\n")
                                country = input("> ")
                                print(
                                    "\nWhich attribute would you like to add or update?\n")
                                attr = input("> ")
                                print(
                                    f"\nEnter the value for {attr} in {country}:\n")
                                val = input("> ")
                                update_item(ddb, table_name, {
                                            attr: val}, "SET", "CountryName", country, None, None)
                                print("Success!")
                                break
                        except Exception as err:
                            print("Error occured.", err)
                            break
                    case "4":
                        print("\nGoodbye!")
                        stopped = True
                        break
                    case "exit":
                        print("\nGoodbye!")
                        stopped = True
                        break
                    case _:
                        print("\nInvalid selection. Enter 1, 2, or 3\n")
                        break
        time.sleep(1)
    except Exception as err:
        print("\nProgram Crashed.", err)


main()
