#!/usr/bin/python3

import os
import subprocess
import configparser
import boto3

cloud_commands = ["locs3cp", "s3loccp", "create_bucket", "create_folder",
                  "chlocn", "cwlocn", "list", "s3copy", "s3delete", "delete_bucket"]


class Shell:
    s3dir = ""
    s3bucket = ""


def init_aws_connection():
    config = configparser.ConfigParser()
    config.read("S5-S3.conf")
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
    #
    #  Set up client and resources
    #

    try:
        s3 = session.resource('s3')

        print("Welcome to the AWS S3 Storage Shell (S5)\nYou are now connected to your S3 Storage")

        return s3

    except:
        print("Welcome to the AWS S3 Storage Shell (S5)\nYou could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3")


def is_cloud_command(command, tokens):
    for cloud_command in cloud_commands:
        if cloud_command == tokens[0]:
            return True
    return False


def exec_commands(command, s3, shell):
    tokens = command.split()
    if not is_cloud_command(command, tokens):
        try:
            subprocess.run(command, shell=True)
        except:
            print("command not found: {}".format(command))
    else:
        match tokens[0]:
            case "locs3cp":
                exec_locs3cp(s3, tokens, shell)
            case "s3loccp":
                exec_s3loccp(s3, tokens, shell)
            case "create_bucket":
                exec_create_bucket(s3, tokens, shell)
            case "create_folder":
                exec_create_folder(s3, tokens, shell)
            case "chlocn":
                exec_chlocn(s3, tokens, shell)
            case "cwlocn":
                exec_cwlocn(s3, tokens, shell)
            case "list":
                exec_list(s3, tokens, shell)
            case "s3copy":
                exec_s3copy(s3, tokens, shell)


def exec_locs3cp(s3, tokens, shell):
    if not shell.s3bucket:
        print("please switch to a valid bucket or specify a bucket in your command")
        return 0
    try:
        if tokens[2][0] != "/":
            s3.Bucket(shell.s3bucket).upload_file(tokens[1], tokens[2])
        else:
            bucket = tokens[2].split("/", 2)[1]
            key = tokens[2].split("/", 2)[2]
            s3.Bucket(bucket).upload_file(tokens[1], key)
    except:
        print("could not copy file")
        return 0
    return 1


def exec_s3loccp(s3, tokens, shell):
    if not shell.s3bucket:
        print("please switch to a valid bucket or specify a bucket in your command")
        return 0
    try:
        if tokens[1][0] != "/" and tokens[1][0] != "~":
            s3.Bucket(shell.s3bucket).download_file(tokens[1], tokens[2])
        else:
            bucket = tokens[1].split("/", 2)[1]
            key = tokens[1].split("/", 2)[2]
            s3.Bucket(bucket).download_file(key, tokens[2])
    except:
        print("could not copy file")
        return 0
    return 1


def exec_create_bucket(s3, tokens, shell):
    if tokens[1][0] != "/" and tokens[1][0] != "~":
        print("please prefix bucket with '/'")
        return 0
    try:
        s3.create_bucket(
            ACL="private",
            Bucket=tokens[1].split("/")[1],
            CreateBucketConfiguration={
                'LocationConstraint': 'ca-central-1'
            })
        return 1
    except Exception as err:
        print("bucket could not be created: ", err)
        return 0


def exec_create_folder(s3, tokens, shell):
    if tokens[1][0] != "/" and tokens[1][0] != "~":
        if shell.s3bucket:
            try:
                if len(tokens[1].split("/")) > 1:
                    preceding_tokens = tokens[1].rsplit("/", 1)[0]
                    key = preceding_tokens + \
                        "/" if preceding_tokens[-1] != "/" else preceding_tokens
                    if not folder_exists(s3, shell.s3bucket, key, shell):
                        print("cannot create folder: No such folder exists")
                        return 0
                key = tokens[1]
                s3.Bucket(shell.s3bucket).put_object(
                    ACL="private", Key=shell.s3dir + "/" + key + "/" if shell.s3dir else "" + key + "/" if key[-1] != "/" else key)
            except Exception as err:
                print("folder could not be created: ", err)
        else:
            print("please switch to a valid bucket or specify a bucket in your command")
    else:
        path_token = tokens[1].split("/")
        try:
            if len(path_token) > 3:
                preceding_tokens = path_token[2].rsplit("/", 1)[0]
                key = preceding_tokens + \
                    "/" if preceding_tokens[-1] != "/" else preceding_tokens
                if not folder_exists(s3, path_token[1], key, shell):
                    print("cannot create folder: No such folder exists")
                    return 0
            key = tokens[1].split("/", 2)[2]
            s3.Bucket(path_token[1]).put_object(
                ACL="private", Key=key + "/" if key[-1] != "/" else key, ContentType="Folder")
        except Exception as err:
            print("folder could not be created: ", err)
    return 1


def exec_chlocn(s3, tokens, shell):
    if(tokens[1] == "/" or tokens[1] == "~"):
        shell.s3bucket = ""
        shell.s3dir = ""
        return 1
    if tokens[1][0] != "/" and tokens[1][0] != "~":
        if shell.s3bucket:
            if folder_exists(s3, shell.s3bucket, tokens[1], shell):
                shell.s3dir += "{}{}".format("/" if shell.s3dir else "",
                                             tokens[1])
                return 1
            print("directory does not exist")
            return 0
        else:
            path_tokens = tokens[1].split("/", 1)
            bucket = path_tokens[0]
            if bucket_exists(s3, bucket):
                shell.s3bucket = bucket
                if len(path_tokens) > 1:
                    if folder_exists(s3, shell.s3bucket, path_tokens[1], shell):
                        shell.s3dir += "{}{}".format(
                            "/" if shell.s3dir else "", path_tokens[1])
                        return 1
                    else:
                        print("directory does not exist")
            else:
                print(
                    "please switch to a valid bucket or specify a bucket in your command")
            return 0

    else:
        path_tokens = tokens[1].split("/")
        if bucket_exists(s3, path_tokens[1]):
            if len(list(filter(lambda x: (x != None and x != "~"), path_tokens))) > 1:
                dir = "".join(path_tokens[2:])
                if folder_exists(s3, path_tokens[1], dir, shell):
                    shell.s3bucket = path_tokens[1]
                    shell.s3dir = "/".join(path_tokens[2:])
                    return 1
            else:
                shell.s3bucket = path_tokens[1]
                shell.s3dir = ""
                return 1
        print("bucket or directory not found")
        return 0


def exec_cwlocn(s3, tokens, shell):
    if not shell.s3bucket:
        print("/")
    else:
        print(shell.s3bucket + "/" + shell.s3dir)
    return 1


def exec_list(s3, tokens, shell):
    try:
        long_flag = False
        if("-l" in tokens):
            long_flag = True
            tokens.remove("-l")
        if len(tokens) > 2:
            print("malformed arguments")
            return 0
        if len(tokens) == 1 or tokens[1] == "/" or tokens[1] == "~":
            if not shell.s3bucket:
                for bucket in s3.buckets.all():
                    print("{}{}".
                    format(s3.BucketAcl(bucket.name).grants[0]["Permission"] + "\t" + str(bucket_size(s3, bucket.name)) + " B\t" if long_flag else "", 
                    bucket.name,
                    ))
            elif not shell.s3dir:
                for object in s3.meta.client.list_objects_v2(Bucket=shell.s3bucket, Delimiter="/").get("CommonPrefixes"):
                    key = object.get("Prefix")
                    print("{}{}".
                    format(s3.ObjectAcl(shell.s3bucket, key).grants[0]["Permission"] + "\t" + str(s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentLength"]) + " B\t" + s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentType"] + "\t" if long_flag else "", 
                    key,
                    ))
            else:
                for object in s3.meta.client.list_objects_v2(Bucket=shell.s3bucket, Delimiter="/", Prefix=shell.s3dir + "/").get("CommonPrefixes"):
                    key = object.get("Prefix")
                    print("{}{}".
                    format(s3.ObjectAcl(shell.s3bucket, key).grants[0]["Permission"] + "\t" + str(s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentLength"]) + " B\t" + s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentType"] + "\t" if long_flag else "", 
                    key.split("/", 1)[-1],
                    ))
        else:
            if tokens[1][0] == "/" or not shell.s3bucket:
                path_tokens = tokens[1].split("/", 2)
                if len(path_tokens) <= 2:
                    for object in s3.meta.client.list_objects_v2(Bucket=path_tokens[1], Delimiter="/").get("CommonPrefixes"):
                        key = object.get("Prefix")
                        print("{}{}".
                        format(s3.ObjectAcl(path_tokens[1], key).grants[0]["Permission"] + "\t" + str(s3.meta.client.head_object(Bucket=path_tokens[1], Key=key)["ContentLength"]) + " B\t" + s3.meta.client.head_object(Bucket=path_tokens[1], Key=key)["ContentType"] + "\t" if long_flag else "", 
                        key,
                        ))
                else:
                    for object in s3.meta.client.list_objects_v2(Bucket=path_tokens[1], Delimiter="/", Prefix=path_tokens[2] + "/").get("CommonPrefixes"):
                        key = object.get("Prefix")
                        print("{}{}".
                        format(s3.ObjectAcl(path_tokens[1], key).grants[0]["Permission"] + "\t" + str(s3.meta.client.head_object(Bucket=path_tokens[1], Key=key)["ContentLength"]) + " B\t" + s3.meta.client.head_object(Bucket=path_tokens[1], Key=key)["ContentType"] + "\t" if long_flag else "", 
                        key.split("/", 1)[-1],
                        ))
            else:
                for object in s3.meta.client.list_objects_v2(Bucket=shell.s3bucket, Delimiter="/", Prefix=tokens[1] + "/").get("CommonPrefixes"):
                    key = object.get("Prefix")
                    print("{}{}".
                    format(s3.ObjectAcl(shell.s3bucket, key).grants[0]["Permission"] + "\t" + str(s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentLength"]) + " B\t" + s3.meta.client.head_object(Bucket=shell.s3bucket, Key=key)["ContentType"] + "\t" if long_flag else "", 
                    key.split("/")[-2] + "/",
                    ))
        return 1

    except Exception as err:
        print("could not list contents of directory: ", err)
        return 0

def exec_s3copy(s3, tokens, shell):
    return


# helpers


def bucket_exists(s3, bucket_name):
    try:
        buckets = [bucket.name for bucket in s3.buckets.all()]
    except:
        print("error requesting resources")
    for bucket in buckets:
        if bucket == bucket_name:
            return True
    return False


def folder_exists(s3, bucket_name, folder_name, shell):
    try:
        folders = s3.Bucket(bucket_name).objects.all()
    except:
        print("error requesting resources")
    for folder in folders:
        if "".join(folder.key.split("/")) == (shell.s3dir + folder_name).replace("/", ""):
            return True
    return False

def bucket_size(s3, bucket_name):
    try:
        total = 0
        for bucket in s3.Bucket(bucket_name).objects.all():
            total += bucket.size
    except:
        print("error requesting resources")
    return total


def main():
    s3 = init_aws_connection()
    shell = Shell()
    while True:
        command = input("S5/{}{}{}> ".format(shell.s3bucket,
                        "/" if shell.s3bucket else "", shell.s3dir))
        if command == "exit" or command == "quit":
            break
        else:
            exec_commands(command, s3, shell)


main()
