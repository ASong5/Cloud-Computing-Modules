#!/usr/bin/python3

# Andrew Song - 1204822
# Assignment 2
# CIS4010
# 02/11/23

import pandas as pd
import json
from decimal import Decimal


def create_table(ddb, table_name, partition_key, partition_key_type="S", sort_key="", sort_key_type="S", global_secondary_index="", global_secondary_index_partition_key="", global_secondary_index_sort_key="", global_secondary_index_type="S", projection_type=""):
    if sort_key:
        if global_secondary_index:
            attr_defn = [{"AttributeName": partition_key, "AttributeType": partition_key_type}, {
                "AttributeName": sort_key, "AttributeType": sort_key_type}, {"AttributeName": global_secondary_index_sort_key, "AttributeType": global_secondary_index_type}]
        else:
            attr_defn = [{"AttributeName": partition_key, "AttributeType": partition_key_type}, {
                "AttributeName": sort_key, "AttributeType": sort_key_type}]
        key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}, {
            "AttributeName": sort_key, "KeyType": "RANGE"}]
    else:
        if global_secondary_index:
            attr_defn = [{"AttributeName": partition_key,
                          "AttributeType": partition_key_type}, {"AttributeName": global_secondary_index_sort_key, "AttributeType": global_secondary_index_type}]
        else:
            attr_defn = [{"AttributeName": partition_key,
                          "AttributeType": partition_key_type}]
        key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]

    if global_secondary_index:
        if global_secondary_index_sort_key:
            global_secondary_indexes = [{"IndexName": global_secondary_index, "KeySchema": [
                {"AttributeName": global_secondary_index_partition_key, "KeyType": "HASH"}, {"AttributeName": global_secondary_index_sort_key, "KeyType": "RANGE"}], "Projection": {"ProjectionType": projection_type}, "ProvisionedThroughput": {"ReadCapacityUnits": 10, "WriteCapacityUnits": 10}}]
        else:
            global_secondary_indexes = [{"IndexName": global_secondary_index, "KeySchema": [
                {"AttributeName": global_secondary_index_partition_key, "KeyType": "HASH"}], "Projection": {"ProjectionType": projection_type}, "ProvisionedThroughput": {"ReadCapacityUnits": 10, "WriteCapacityUnits": 10}}]
        params = {"TableName": table_name, "AttributeDefinitions": attr_defn, "KeySchema": key_schema, "GlobalSecondaryIndexes": global_secondary_indexes,
                  "ProvisionedThroughput": {"ReadCapacityUnits": 10, "WriteCapacityUnits": 10}}
    else:
        params = {"TableName": table_name, "AttributeDefinitions": attr_defn, "KeySchema": key_schema,
                  "ProvisionedThroughput": {"ReadCapacityUnits": 10, "WriteCapacityUnits": 10}}
    try:
        ddb.create_table(**params)
        ddb.meta.client.get_waiter("table_exists").wait(
            TableName=table_name, WaiterConfig={"Delay": 1})
    except ddb.meta.client.exceptions.ResourceInUseException:
        pass
    except Exception:
        raise


def delete_table(ddb, table_name):
    try:
        ddb.meta.client.delete_table(TableName=table_name)
        ddb.meta.client.get_waiter("table_not_exists").wait(
            TableName=table_name, WaiterConfig={"Delay": 1})
    except Exception:
        raise


def load_records(ddb, table_name, df):
    table = ddb.Table(table_name)
    ddb.meta.client.get_waiter("table_exists").wait(
        TableName=table_name, WaiterConfig={"Delay": 1})
    try:
        with table.batch_writer() as batch:
            for index, row in df.iterrows():
                batch.put_item(json.loads(row.to_json(), parse_float=Decimal))
    except Exception:
        raise


def add_record(ddb, table_name, record):
    ddb.meta.client.get_waiter("table_exists").wait(
        TableName=table_name, WaiterConfig={"Delay": 1})
    try:
        ddb.put_item(TableName=table_name, Item=record)
    except Exception:
        raise


def delete_record(ddb, table_name, partition_key, partition_key_val, sort_key="", sort_key_val=""):
    if ddb.Table(table_name).table_status != "Active":
        return
    try:
        if (sort_key):
            ddb.meta.client.delete_item(TableName=table_name, Key={partition_key:
                                        partition_key_val, sort_key: sort_key_val})
        else:
            ddb.meta.client.delete_item(TableName=table_name, Key={
                                        partition_key: partition_key_val})
    except Exception:
        raise


def dump(ddb, table_name):
    try:
        data = ddb.meta.client.scan(
            TableName=table_name, Select="ALL_ATTRIBUTES")
        for item in data["Items"]:
            for key in item:
                item[key] = item[key]["S"]
        data = pd.DataFrame(data["Items"])
        return data
    except Exception:
        raise


def query_item(ddb, table_name, partition_key="", partition_value="", sort_key="", sort_key_val="", attributes=""):
    try:
        if partition_key:
            if sort_key:
                item = ddb.meta.client.get_item(TableName=table_name, Key={
                                                partition_key: partition_value, sort_key: sort_key_val})
            else:
                item = ddb.meta.client.get_item(TableName=table_name, Key={
                                                partition_key: partition_value})
        else:
            if attributes:
                item = ddb.meta.client.scan(
                    TableName=table_name, ProjectionExpression=attributes)
            else:
                item = ddb.meta.client.scan(TableName=table_name)
        return item
    except Exception:
        raise


def update_item(ddb, table_name, new_attr, update_type, partition_key, partition_value, sort_key="", sort_key_val=""):
    try:
        if sort_key:
            ddb.meta.client.update_item(TableName=table_name, Key={
                partition_key: partition_value, sort_key: sort_key_val},
                UpdateExpression=f'SET {list(new_attr.keys())[0]} = :val',
                ExpressionAttributeNames={
                    "#attr": str(list(new_attr.keys())[0])},
                ExpressionAttributeValues={":val": list(new_attr.values())[0]})
        else:
            ddb.meta.client.update_item(TableName=table_name, Key={
                partition_key: partition_value},
                UpdateExpression='SET #attr = :val',
                ExpressionAttributeNames={
                    "#attr": str(list(new_attr.keys())[0])},
                ExpressionAttributeValues={":val": list(new_attr.values())[0]}
            )
    except Exception:
        raise


def list_tables(ddb):
    try:
        return ddb.meta.client.list_tables()
    except Exception as err:
        raise

# helpers


def parse_csv_records(csv):
    records = []
    for row in csv:
        record = list(filter(None, row.replace("\n", "").split(",")))
        records.append(record)
    return records
