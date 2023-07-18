# Cloud-Computing-Modules
Cloud Computing assignments - CIS4010 - University of Guelph 2023

# A1

Shell program that establishes a connection with AWS S3 via Boto3 SDK to perform CRUD tasks and other generic shell operations; e.g., creating/deleting buckets, transferring/copying objects between buckets or sub-directories, changing current working directories, listing objects, etc.

The shell emulates the nuances and functionality of a regular Linux shell. So despite the flat structure of the S3 file system, the shell facilitates and performs operations in a manner that is conducive to modern hierarchical file systems.

# A2

Library of modules to work with AWS DynamoDB. The suite of functions found in this assignment allows the user to perform CRUD operations on their DynamoDB tables with country-related and GDP-related data (provided by prof). Additionally, it also has functions for querying and listing objects. It also includes a console application that facilitates and streamlines these operations for the user. In addition, the application can generate two types of reports from data in the tables: 
- Report A: data for a specific country. E.g.,
  
~~~
Canada
[Official Name: Canada]
+----------------------------------------------+
| Area: 9970610 sq km (1)                      |
+----------------------------------------------+
| Official/National Languages: English, French |
| Capital City: Ottawa                         |
+----------------------------------------------+

Population
+--------+--------------+-------------------+----------------------+---------------------------+
|   Year | Population   |   Population Rank |   Population Density |   Population Density Rank |
+========+==============+===================+======================+===========================+
|   1970 | 21,374,326   |                 6 |                 2.14 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1971 | 21,723,460   |                 6 |                 2.18 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1972 | 22,072,194   |                 6 |                 2.21 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1973 | 22,415,322   |                 6 |                 2.25 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1974 | 22,745,903   |                 6 |                 2.28 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1975 | 23,059,265   |                 6 |                 2.31 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
|   1976 | 23,354,586   |                 6 |                 2.34 |                        38 |
+--------+--------------+-------------------+----------------------+---------------------------+
...
~~~

- Report B: data for all countries on a specific date. E.g.,
~~~
Global Report
Year: 1981
Number of Countries: 40

Table of Countries Ranked by Population (largest to smallest)
+----------------------------------+---------------+--------+
| Country Name                     | Population    |   Rank |
+==================================+===============+========+
| China                            | 1,014,022,212 |      1 |
+----------------------------------+---------------+--------+
| Brazil                           | 123,570,327   |      2 |
+----------------------------------+---------------+--------+
| Bangladesh                       | 81,767,515    |      3 |
+----------------------------------+---------------+--------+
| Argentina                        | 28,338,515    |      4 |
+----------------------------------+---------------+--------+
| Colombia                         | 27,496,617    |      5 |
+----------------------------------+---------------+--------+
| Canada                           | 24,668,167    |      6 |
+----------------------------------+---------------+--------+
...

Table of Countries Ranked by Area (largest to smallest)
+----------------------------------+-----------+--------+
| Country Name                     | Area      |   Rank |
+==================================+===========+========+
| Canada                           | 9,970,610 |      1 |
+----------------------------------+-----------+--------+
| China                            | 9,596,961 |      2 |
+----------------------------------+-----------+--------+
| Brazil                           | 8,514,877 |      3 |
+----------------------------------+-----------+--------+
| Australia                        | 7,741,220 |      4 |
+----------------------------------+-----------+--------+
...

Table of Countries Ranked by Density (largest to smallest)
+----------------------------------+----------------------------+--------+
| Country Name                     |   Density (people / sq km) |   Rank |
+==================================+============================+========+
| Barbados                         |                     589.07 |      1 |
+----------------------------------+----------------------------+--------+
| Bangladesh                       |                     567.84 |      2 |
+----------------------------------+----------------------------+--------+
| Bahrain                          |                     539.08 |      3 |
+----------------------------------+----------------------------+--------+
| Belgium                          |                     323.66 |      4 |
+----------------------------------+----------------------------+--------+
| Burundi                          |                     153.28 |      5 |
+----------------------------------+----------------------------+--------+
| Comoros                          |                     142.11 |      6 |
+----------------------------------+----------------------------+--------+
...

GDP Per Capita for all Countries
1970's Table
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Country Name                     |   1970 |   1971 |   1972 |   1973 |   1974 |   1975 |   1976 |   1977 |   1978 |   1979 |
+==================================+========+========+========+========+========+========+========+========+========+========+
| Albania                          |   1053 |   1058 |   1064 |   1069 |   1076 |   1082 |   1090 |   1096 |   1105 |    903 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Algeria                          |    356 |    361 |    469 |    588 |    821 |    937 |   1039 |   1194 |   1457 |   1780 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Andorra                          |   4098 |   4426 |   5336 |   6761 |   7996 |   9071 |   9050 |   9807 |  11552 |  14956 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Angola                           |    646 |    664 |    657 |    772 |    832 |    591 |    547 |    577 |    622 |    668 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Antigua and Barbuda              |    528 |    639 |    880 |   1231 |   1323 |   1363 |   1138 |   1300 |   1475 |   1819 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Argentina                        |   1423 |   1676 |   1554 |   1722 |   1906 |   1997 |   2083 |   2313 |   2356 |   2691 |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
| Armenia                          |        |        |        |        |        |        |        |        |        |        |
+----------------------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+
...
~~~

# A3

Automation script for the dynamic generation of GCP and Azure VMs. Given a file with various input parameters, the script can connect to GCP and Azure and can generate and fire up VMs seamlessly and without any work by the user. Once the script terminates, a report log is generated with any necessary information about the VM creation.

# A4

AWS lambda handler deployed via docker container image to allow for subscribed users of an S3 bucket to automatically receive their own copy of objects that are transferred into the bucket.
