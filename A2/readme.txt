# Andrew Song - 1204822
# Assignment 2
# CIS4010
# 02/11/23

Notes and Limitations
- All programs were developed with Python 3.10.6
    - Any version of python 3.10 and higher should work. 
    - The school's version of python (3.7?) will not work. Please update python before running the program.
- To install the required dependencies and packages, use the command "pip install -r requirements.txt" before running the program
- Ensure you have a configuration file named "DDB.conf" in your current working directory that contains your DDB credentials.
    - Ensure the region attribute is "ca-central-1".
- Please open the reports in notepad++ or any other text editor that retains fixed column widths (like the Visual Studio Code editor)
    - The formatting will be off when opened in a program like vanilla notepad.
- The DynamoDB modules are contained within the file ddb_modules.py
- The report generation logic is contained within report_gen.py
- The driver CLI program is contained within A2.py; this includes the initial load logic.
- All functionality to interface with our dyanmodb tables based on the specs should be working.
- The generated reports should be more or less identical in format to the templates provided in the courselink assignment description
- Although I did not need to use them for this assignment, the functions in ddb_modules allow for optional sort keys 
- The only change made to the initial .csv files provided was the missing header (columns) from un_shortlist.csv
- The tables created in DyanamoDB are "{user_name}_countries", "{user_name}_population", "{user_name}_gdp", where the gdp table contains economic 
data and the population table does not.
- The missing info functionality is implemented via a simple CLI. 
    - The CLI does not contain a lot of error handling, and may be a bit fragile since CLI input validation was not the focus of 
    the assignment. So I did not spend a lot of time on it.
        - Note that inputs are case sensitive (e.g., country names)
    - Please read the instructions carefully and try to only input non-erroneous information
- The reports were built using the pandas and tabulate libraries. Does not generate a PDF; simply redirects the output to a file in the current
directory.
- There is a brief pre-processing stage in A2.py that re-generates shortlist_languages.csv to deal with the comma separated shortlist_languages

How to use modules:
- The following are the function signatures:

    create_table(ddb, table_name, partition_key, partition_key_type="S", sort_key="", sort_key_type="S", global_secondary_index="", global_secondary_index_partition_key="", global_secondary_index_sort_key="", global_secondary_index_type="S", projection_type="")

    delete_table(ddb, table_name)

    load_records(ddb, table_name, df)

    add_record(ddb, table_name, record)

    delete_record(ddb, table_name, partition_key, partition_key_val, sort_key="", sort_key_val="")

    dump(ddb, table_name)

    query_item(ddb, table_name, partition_key="", partition_value="", sort_key="", sort_key_val="", attributes="")

    update_item(ddb, table_name, new_attr, update_type, partition_key, partition_value, sort_key="", sort_key_val="")

    list_tables(ddb)

- Many functions contain optional/default parameters. If not needed, simply pass in None or an empty string (""). Otherwise, default values will
be used.
- All functions require a ddb parameter, i.e., your dynamodb resource object.
- If a sort key is used, it must be specified along with the partition key. Otherwise an error will be thrown.
- The table_name parameter should be prefixed with the username of the account
    - user_name = session.client("sts").get_caller_identity()['UserId']  <-- do this to get the user name

How to generate report A:
- Type ./A2.py to run the CLI program
- Follow the instructions
- Sample run:
    > ./A2.py
    Connecting to AWS DynamoDB... Please wait
    Connected to AWS DynamoDB
    Creating tables. Please wait...

    Welcome to A2 - DynamoDB Modules with Boto3 and Report Generator

    Choose an action to perform:
    (1) Generate Report A
    (2) Generate Report B
    (3) Add Missing Information to Table
    (4) To exit the application. Or type 'exit'
    > 1

    Enter the name of the country you would like to generate a report for.
    > Canada
    Success!

- The report should be placed in your current working directory as "Report A - {country_name}.txt"
- Please open the report in notepad++ or any other text editor that retains fixed column widths (like the Visual Studio Code editor)
    - The formatting will be off when opened in a program like vanilla notepad.

How to generate report B:
- Type ./A2.py to run the CLI program
- Follow the instructions
- Sample run:
    > ./A2.py
    Connecting to AWS DynamoDB... Please wait
    Connected to AWS DynamoDB
    Creating tables. Please wait...

    Welcome to A2 - DynamoDB Modules with Boto3 and Report Generator

    Choose an action to perform:
    (1) Generate Report A
    (2) Generate Report B
    (3) Add Missing Information to Table
    (4) To exit the application. Or type 'exit'
    > 2

    Enter the year you would like to generate a report for.
    > 1994
    Success!

- The report should be placed in your current working directory as "Report B - {year}.txt"
- Please open the report in notepad++ or any other text editor that retains fixed column widths (like the Visual Studio Code editor)
    - The formatting will be off when opened in a program like vanilla notepad.

How to add missing information:
- Type ./A2.py to run the CLI program
- Follow the instructions
- Sample run:
    > ./A2.py
    Connecting to AWS DynamoDB... Please wait
    Connected to AWS DynamoDB
    Creating tables. Please wait...

    Welcome to A2 - DynamoDB Modules with Boto3 and Report Generator

    Choose an action to perform:
    (1) Generate Report A
    (2) Generate Report B
    (3) Add Missing Information to Table
    (4) To exit the application. Or type 'exit'
    > 3
    
    Tables:

    (1) AIDAZMTTOSN5ZFW36HJBM_countries
    (2) AIDAZMTTOSN5ZFW36HJBM_gdp
    (3) AIDAZMTTOSN5ZFW36HJBM_population

    Select a table by number

    > 1
    Which country would you like to add missing information for?

    > Canada

    Which attribute would you like to add or update?

    > Area

    Enter the value for Area in Canada:

    > 123456
    Success!

