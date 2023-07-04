#!/usr/bin/python3

# Andrew Song - 1204822
# Assignment 1
# CIS4010
# 01/30/23

import os
from pathlib import Path
import re
import subprocess
import configparser
import boto3


class Shell:
    s3 = None
    s3loc = "/"
    command = ""
    tokens = ""


cloud_commands = ["locs3cp", "s3loccp", "create_bucket", "create_folder",
                  "chlocn", "cwlocn", "list", "s3copy", "s3delete", "delete_bucket"]


def init_aws_connection(shell):
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
        shell.s3 = session.resource('s3')

        print("Welcome to the AWS S3 Storage Shell (S5)\nYou are now connected to your S3 Storage")

    except:
        print("Welcome to the AWS S3 Storage Shell (S5)\nYou could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3")


def is_cloud_command(tokens):
    for cloud_command in cloud_commands:
        if cloud_command == tokens[0]:
            return True
    return False


def exec_commands(shell):
    shell.tokens = shell.command.split()
    if not is_cloud_command(shell.tokens):
        try:
            if shell.tokens[0] == "cd":
                os.chdir(shell.tokens[1])
            else:
                subprocess.run(shell.command, shell=True)
        except:
            print("command not found: {}".format(shell.command))
    else:
        match shell.tokens[0]:
            case "locs3cp":
                exec_locs3cp(shell)
            case "s3loccp":
                exec_s3loccp(shell)
            case "create_bucket":
                exec_create_bucket(shell)
            case "create_folder":
                exec_create_folder(shell)
            case "chlocn":
                exec_chlocn(shell)
            case "cwlocn":
                exec_cwlocn(shell)
            case "list":
                exec_list(shell)
            case "s3copy":
                exec_s3copy(shell)
            case "s3delete":
                exec_s3delete(shell)
            case "delete_bucket":
                exec_delete_bucket(shell)


def exec_locs3cp(shell):
    if len(shell.tokens) != 3:
        print("incorrect number of arguments")
        return 0
    try:
        tokens = list(filter(None, shell.tokens[2].rsplit("/", 1)))
        if len(tokens) == 1 and tokens[0][0] != "/":
            cloud_path = parse_path(shell, ".")
        else:
            cloud_path = parse_path(shell, tokens[0])
        dir = get_dir_from_path(cloud_path)
        if dir:
            shell.s3.Bucket(get_bucket_from_path(cloud_path)).upload_file(
                shell.tokens[1], dir + "/" + tokens[-1])
        else:
            shell.s3.Bucket(get_bucket_from_path(cloud_path)
                            ).upload_file(shell.tokens[1], tokens[-1])
    except:
        print("unsuccessful copy")
        return 0
    return 1


def exec_s3loccp(shell):
    if len(shell.tokens) != 3:
        print("incorrect number of arguments")
        return 0
    try:
        # tokens = list(filter(None, shell.tokens[1].rsplit("/", 1)))
        cloud_path = parse_path(shell, shell.tokens[1])
        dir = get_dir_from_path(cloud_path)
        if dir:
            shell.s3.Bucket(get_bucket_from_path(cloud_path)
                            ).download_file(dir, shell.tokens[2])
        # else:
        #     shell.s3.Bucket(get_bucket_from_path(cloud_path)).download_file(shell.tokens[1], shell.tokens[2])
    except Exception as err:
        print("unsuccessful copy", err)
        return 0
    return 1


def exec_create_bucket(shell):
    if len(shell.tokens) != 2:
        print("incorrect number of arguments")
        return 0
    try:
        shell.s3.create_bucket(
            ACL="private",
            Bucket=shell.tokens[1],
            CreateBucketConfiguration={
                'LocationConstraint': 'ca-central-1'
            })
    except Exception as err:
        print("bucket could not be created: ", err)
        return 0
    return 1


def exec_create_folder(shell):
    if len(shell.tokens) != 2:
        print("incorrect number of arguments")
        return 0
    try:
        tokens = list(filter(None, shell.tokens[1].rsplit("/", 1)))
        if len(tokens) == 1 and shell.tokens[1][0] != "/":
            cloud_path = parse_path(shell, ".")
        else:
            cloud_path = parse_path(shell, tokens[0])
        dir = get_dir_from_path(cloud_path)
        if dir:
            shell.s3.Bucket(get_bucket_from_path(cloud_path)).put_object(
                ACL="private", Key=dir + "/" + tokens[-1] + "/", ContentType="Folder")
        else:
            shell.s3.Bucket(get_bucket_from_path(cloud_path)).put_object(
                ACL="private", Key=tokens[-1] + "/", ContentType="Folder")
    except Exception as err:
        print("folder could not be created.", err)
        return 0
    return 1


def exec_chlocn(shell):
    if len(shell.tokens) != 2:
        print("incorrect number of arguments")
        return 0
    path = parse_path(shell, shell.tokens[1])
    if path:
        shell.s3loc = path
        return 1
    else:
        return 0


def exec_cwlocn(shell):
    if len(shell.tokens) != 1:
        print("incorrect number of arguments")
        return 0
    print(shell.s3loc)
    return 1


def exec_list(shell):
    long_flag = False
    if "-l" in shell.tokens:
        shell.tokens.remove("-l")
        long_flag = True

    if len(shell.tokens) > 2:
        print("incorrect number of arguments")
        return 0

    try:
        if len(shell.tokens) == 1:
            cloud_path = parse_path(shell, ".")
            curr_bucket = get_bucket_from_path(cloud_path)
            dir = get_dir_from_path(cloud_path)
            if not curr_bucket and not dir:
                for bucket in shell.s3.buckets.all():
                    print("{}{}".
                          format(shell.s3.BucketAcl(bucket.name).grants[0]["Permission"] + "\t" + str(bucket_size(shell, bucket.name)) + " B\t" if long_flag else "",
                                 bucket.name,
                                 ))
            else:
                curr_bucket = get_bucket_from_path(cloud_path)
                for object in shell.s3.meta.client.list_objects_v2(Bucket=curr_bucket, Delimiter="/", Prefix=dir + "/" if dir else "").get("Contents"):
                    key = object.get("Key")
                    print("{}{}".
                          format(shell.s3.ObjectAcl(curr_bucket, key).grants[0]["Permission"] + "\t" + str(shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=key)["ContentLength"]) + " B\t" + shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=key)["ContentType"] + "\t" if long_flag else "",
                                 list(filter(None, key.split("/")))[-1]
                                 ))
                for object in shell.s3.meta.client.list_objects_v2(Bucket=curr_bucket, Delimiter="/", Prefix=dir + "/" if dir else "").get("CommonPrefixes"):
                    prefix = object.get("Prefix")
                    print("{}{}".
                          format(shell.s3.ObjectAcl(curr_bucket, prefix).grants[0]["Permission"] + "\t" + str(shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=prefix)["ContentLength"]) + " B\t" + shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=prefix)["ContentType"] + "\t" if long_flag else "",
                                 list(filter(None, prefix.split("/")))[-1]
                                 ))
        else:
            cloud_path = parse_path(shell, shell.tokens[1])
            curr_bucket = get_bucket_from_path(cloud_path)
            dir = get_dir_from_path(cloud_path)
            objects = shell.s3.meta.client.list_objects_v2(Bucket=curr_bucket, Delimiter="/", Prefix=dir + "/" if dir else "").get("Contents")
            folders = shell.s3.meta.client.list_objects_v2(Bucket=curr_bucket, Delimiter="/", Prefix=dir + "/" if dir else "").get("CommonPrefixes")

            if objects:
                for object in objects:
                    key = object.get("Key")
                    print("{}{}".
                        format(shell.s3.ObjectAcl(curr_bucket, key).grants[0]["Permission"] + "\t" + str(shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=key)["ContentLength"]) + " B\t" + shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=key)["ContentType"] + "\t" if long_flag else "",
                                list(filter(None, key.split("/")))[-1]
                                ))
            if folders:
                for object in folders:
                    prefix = object.get("Prefix")
                    print("{}{}".
                        format(shell.s3.ObjectAcl(curr_bucket, prefix).grants[0]["Permission"] + "\t" + str(shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=prefix)["ContentLength"]) + " B\t" + shell.s3.meta.client.head_object(Bucket=curr_bucket, Key=prefix)["ContentType"] + "\t" if long_flag else "",
                                list(filter(None, prefix.split("/")))[-1]
                                ))

    except Exception as err:
        print("cannot list contents of this S3 location.", err)
        return 0
    return 1


def exec_s3copy(shell):
    try:
        if len(shell.tokens) != 3:
            print("incorrect number of arguments")
            return 0

        # src_tokens = list(filter(None, shell.tokens[1].rsplit("/", 1)))
        dest_tokens = list(filter(None, shell.tokens[2].rsplit("/", 1)))

        src_path = parse_path(shell, shell.tokens[1])
        if len(dest_tokens) == 1 and shell.tokens[2][0] != "/" and shell.tokens[2][0] != ".":
            dest_path = parse_path(shell, ".")
        else:
            dest_path = parse_path(shell, dest_tokens[0])

        src_dir = folder_exists(shell, get_bucket_from_path(
            src_path), get_dir_from_path(src_path))
        dest_dir = get_dir_from_path(dest_path)

        copy_source = {"Bucket": get_bucket_from_path(
            src_path), "Key": src_dir}
        copy_dest = shell.s3.Bucket(get_bucket_from_path(dest_path)).Object(
            (dest_dir + "/" + dest_tokens[-1] if dest_dir else dest_tokens[-1]) + ("/" if src_dir[-1] == "/" else ""))

        copy_dest.copy(copy_source)
    except Exception as err:
        print("cannot copy object.", err)
        return 0
    return 1


def exec_s3delete(shell):
    if len(shell.tokens) != 2:
            print("incorrect number of arguments")
            return 0
    try:
        cloud_path = parse_path(shell, shell.tokens[1])
        curr_bucket = get_bucket_from_path(cloud_path)
        dir = get_dir_from_path(cloud_path)
        if dir == get_dir_from_path(shell.s3loc):
            print("cannot delete current working directory, consider using chlocn first")
            return 0
        delete_key = folder_exists(shell, curr_bucket, dir)

        if curr_bucket and not dir:
            print("cannot delete bucket - use 'delete_bucket'")
            return 0
        if delete_key[-1] == "/":
            flag = is_folder_empty(shell, curr_bucket, delete_key)
            if flag == -1 or not flag:
                raise Exception

        shell.s3.meta.client.delete_object(Bucket=curr_bucket, Key=delete_key)

    except Exception as err:
        print("cannot delete object.", err)
        return 0
    return 1

def exec_delete_bucket(shell):
    if len(shell.tokens) != 2:
            print("incorrect number of arguments")
            return 0
    try:
        bucket = get_bucket_from_path(parse_path(shell, shell.tokens[1]))
        if bucket == get_bucket_from_path(shell.s3loc):
            print("cannot delete bucket you are currently in, consider using chlocn first")
            return 0
        shell.s3.Bucket(bucket).delete()
    except Exception as err:
        print("could not delete bucket.", err)
        return 0
    return 1


# helpers

def get_bucket_from_path(path):
    if path == "/":
        return ""
    else:
        return list(filter(None, path.split("/")))[0]


def get_dir_from_path(path):
    tokens = list(filter(None, path.split("/", 2)))
    if path == "/" or len(tokens) < 2:
        return ""
    else:
        return tokens[1]


def is_folder_empty(shell, bucket, path):
    total = 0
    try:
        total = shell.s3.meta.client.list_objects_v2(
            Bucket=bucket, Delimiter="/", Prefix=path).get("KeyCount")
    except Exception as err:
        print("directory is not empty.", err)
        return -1
    return True if total == 1 else False


# handles "." and ".." and determines if path is absolute or relative


def clean_path(shell, path):
    if path == "/" or path == "~":
        return "/"
    if path[0] == "/" or path[0] == "~":
        new_path = str(Path("/" + path).resolve())
    else:
        new_path = str(Path(shell.s3loc + "/" + path).resolve())
    new_path = re.sub(r"^\.|\.$|^\.$", dir if dir else "/", new_path)
    return new_path


def parse_path(shell, tokens):
    path = ""
    try:
        cleaned_path = clean_path(shell, tokens)
        # if absolute path
        if tokens[0] == "/":
            # parse path into tokens
            path_tokens = list(filter(None, cleaned_path.split("/", 2)))
            # if there is more than one token, we know that there is a bucket and some directory
            if len(path_tokens) > 1:
                # check if that directory exists
                if folder_exists(shell, path_tokens[0], path_tokens[1]):
                    path = str(Path(cleaned_path).resolve())
                else:
                    print("folder does not exist")
            # if there is only one token, we know it must be the bucket
            elif len(path_tokens) == 1:
                # check if the bucket exists
                if bucket_exists(shell, path_tokens[0]):
                    path = str(Path(cleaned_path).resolve())
                else:
                    print("bucket does not exist")
            # if there are zero tokens, only "/" was provided so go to root
            else:
                path = "/"
        # if relative path
        else:
            # get current bucket from s3loc
            curr_bucket = get_bucket_from_path(shell.s3loc)
            # get directory from the cleaned path
            dir = get_dir_from_path(cleaned_path)
            # if we are in a bucket
            if curr_bucket and dir:
                if folder_exists(shell, curr_bucket, dir):
                    path = str(
                        Path(cleaned_path).resolve())
                else:
                    print("folder does not exist")
            else:
                path_tokens = list(filter(None, cleaned_path.split("/", 2)))
                if len(path_tokens) > 1:
                    if folder_exists(shell, path_tokens[0], path_tokens[1]):
                        path = str(
                            Path(cleaned_path).resolve())
                    else:
                        print("folder does not exist")
                elif len(path_tokens) == 1:
                    if bucket_exists(shell, path_tokens[0]):
                        path = str(
                            Path(cleaned_path).resolve())
                    else:
                        print("bucket does not exist")
                else:
                    path = "/"
    except Exception as err:
        print("parsing error", err)
    return path


def bucket_exists(shell, bucket_name):
    try:
        buckets = [bucket.name for bucket in shell.s3.buckets.all()]
    except Exception as err:
        print("error requesting resources", err)
        return 0
    for bucket in buckets:
        if bucket == bucket_name:
            return True
    return False


def folder_exists(shell, bucket_name, path):
    try:
        folders = shell.s3.Bucket(bucket_name).objects.all()
    except:
        print("error requesting resources")
    for folder in folders:
        if folder.key == path or folder.key == path + "/":
            return folder.key
    return False


def bucket_size(shell, bucket_name):
    try:
        total = 0
        for bucket in shell.s3.Bucket(bucket_name).objects.all():
            total += bucket.size
    except:
        print("error requesting resources")
    return total


def main():
    shell = Shell()
    init_aws_connection(shell)

    while True:
        bucket = get_bucket_from_path(shell.s3loc)
        dir = get_dir_from_path(shell.s3loc)
        shell.command = input("S5/{}{}{}> ".format(bucket,
                                                   "/" if bucket else "", dir))
        if shell.command == "exit" or shell.command == "quit":
            break
        else:
            exec_commands(shell)


main()
