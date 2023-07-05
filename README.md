# Cloud-Computing-Modules
Cloud Computing assignments - CIS4010 - University of Guelph 2023

# A1

Shell program that establishes a connection with AWS S3 via Boto3 SDK to perform CRUD tasks and other generic shell operations; e.g., creating/deleting buckets, transferring/copying objects between buckets or sub-directories, changing current working directories, listing objects, etc.

The shell emulates the nuances and functionality of a regular Linux shell. So despite the flat structure of the S3 file system, the shell facilitates and performs operations in a manner that is conducive to modern hierarchical file systems.

# A2

Library of modules to work with AWS DynamoDB. The suite of functions found in this assignment allows the user to perform CRUD operations on their DynamoDB tables with country-related and GDP-related data (provided by prof). Additionally, it also has functions for querying and listing objects. It also includes a console application that facilitates and streamlines these operations for the user. In addition, the application can generate two types of reports from data in the tables: 
- Report A: data for a specific country
- Report B: data for all countries on a specific date

# A3

Automation script for the dynamic generation of GCP and Azure VMs. Given a file with various input parameters, the script can connect to GCP and Azure and can generate and fire up VMs seamlessly and without any work by the user. Once the script terminates, a report log is generated with any necessary information about the VM creation.

# A4

AWS lambda handler deployed via docker container image to allow for subscribed users of an S3 bucket to automatically receive their own copy of objects that are transferred into the bucket.
