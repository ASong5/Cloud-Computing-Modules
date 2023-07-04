#!/usr/bin/python3

# Andrew Song - 1204822
# Assignment 3
# CIS4010
# 03/12/23
import configparser
import re
import subprocess
import datetime
import copy
import getpass
import os

max_vms = 10
doc_params = ["purpose", "os", "team", "project"]


def read_config(azure_conf, gcp_conf):
    if not azure_conf or not gcp_conf:
        print("Error: Missing or invalid config file")
        return

    azure_config = configparser.ConfigParser()
    azure_config.read(azure_conf)
    gcp_config = configparser.ConfigParser()
    gcp_config.read(gcp_conf)

    if (len(azure_config.sections()) > max_vms or len(gcp_config.sections()) > max_vms):
        print(f"Error: Too many VMs (max {max_vms})")
        return

    azure_settings = []
    admin_password_pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{12,123}$')
    for section in azure_config.sections():
        try:
            if azure_config[section]["os"] == "windows":
                if not azure_config.has_section("admin-password"):
                    password = input(
                        f"Enter admin-password for {azure_config[section]['name']}: ")
                    azure_config[section]["admin-password"] = password
                    if not admin_password_pattern.match(azure_config[section]["admin-password"]):
                        print(
                            "Error: admin-password does not adhere to specifications")
                        return
            vm_settings = {}
            for key, val in azure_config.items(section):
                vm_settings[key] = val
            azure_settings.append(vm_settings)
        except Exception as err:
            print("Invalid configuration file:", err)

    gcp_settings = []
    gcp_vm_name_pattern = re.compile(r"[a-z0-9]+")
    for section in gcp_config.sections():
        try:
            if not gcp_vm_name_pattern.match(gcp_config[section]["name"]):
                print("Error: vm name does not adhere to specifications")
                return
            vm_settings = {}
            for key, val in gcp_config.items(section):
                vm_settings[key] = val
            gcp_settings.append(vm_settings)
        except Exception as err:
            print("Invalid configuration file:", err)

    settings = {"azure": azure_settings, "gcp": gcp_settings}

    return settings


def execute_commands(settings, azure_ports, gcp_ports):
    updated_settings = copy.deepcopy(settings)
    for setting in settings["azure"]:
        command = "az vm create"
        for key, val in setting.items():
            if key not in doc_params:
                command += f" --{key} {val}"
        command += " --generate-ssh-keys"

        try:
            print(f"Checking if {setting['name']} exists...")
            subprocess.check_output(
                f"az vm show -n {setting['name']} -g {setting['resource-group']}", shell=True)
        except subprocess.CalledProcessError as e:
            no_resource_group_err = re.compile(r"Code: ResourceGroupNotFound")
            no_resource_err = re.compile(r"Code: ResourceNotFound")
            if not no_resource_group_err.match(e.output.decode()):
                print(
                    f"Creating resource group: {setting['resource-group']}")
                subprocess.run(
                    f"az group create -n {setting['resource-group']} -l {setting['location']}", shell=True)
                print(f"Resource-group {setting['resource-group']} created.")
                print(f"Executing command: {command}")
                subprocess.run(command, shell=True)
                print(f"Successfully created {setting['name']}")
            elif not no_resource_err.match(e.output.decode()):
                print(f"Executing command: {command}")
                subprocess.check_output(command, shell=True)
                print(f"Successfully created {setting['name']}")
        else:
            print(f"The VM {setting['name']} already exists.")
            updated_settings["azure"].remove(setting)
            continue
        if len(azure_ports) > 0:
            open_port_command = f"az vm open-port -n {setting['name']} -g {setting['resource-group']} --port "
            for port in azure_ports[0:len(azure_ports) - 1]:
                open_port_command += port + ","
            open_port_command += azure_ports[-1]
            print("Waiting for VM to finalize creation...")
            while True:
                provisioning_state = subprocess.check_output(
                    f"az vm show -n {setting['name']} -g {setting['resource-group']} --query 'provisioningState' -o tsv",
                    shell=True,
                    text=True).strip()
                if provisioning_state == "Succeeded":
                    break
            print(f"Opening ports: {open_port_command}")
            subprocess.check_output(open_port_command, shell=True)
            print("Ports successfully opened.")

    for setting in settings["gcp"]:
        command = f"gcloud compute instances create {setting['name']}"
        for key, val in setting.items():
            if key not in doc_params and key != "name":
                command += f" --{key}={val}"

        try:
            print(f"Checking if {setting['name']} exists...")
            subprocess.check_output(
                f"gcloud compute instances describe {setting['name']} --zone {setting['zone']}", shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            no_vm_err = re.compile(r"was not found")
            if not no_vm_err.match(e.output.decode()):
                print(f"Executing command: {command}")
                try:
                    subprocess.check_output(command, shell=True)
                except subprocess.CalledProcessError as e2:
                    print("Error:", e2)
                    return
                print(f"Successfully created {setting['name']}")
        else:
            print(f"The VM {setting['name']} already exists.")
            updated_settings["gcp"].remove(setting)
            continue

        if len(gcp_ports) > 0:
            tcp_ports = ','.join([f'tcp:{port}' for port in gcp_ports])
            udp_ports = ','.join([f'udp:{port}' for port in gcp_ports])
            open_port_command = f"gcloud compute firewall-rules create firewall-rule --allow {tcp_ports},{udp_ports} --target-tags {setting['name']}"
            print("Waiting for VM to finalize creation...")
            while True:
                vm_info = subprocess.check_output(f"gcloud compute instances describe {setting['name']} --zone {setting['zone']} --format 'value(status)'", shell=True, text=True).strip()
                if vm_info == "RUNNING":
                    break
            print(f"Opening ports: {open_port_command}")
            try:
                subprocess.check_call("gcloud compute firewall-rules describe firewall-rule", shell=True)
            except subprocess.CalledProcessError:
                print("Creating firewall rules...")
                subprocess.check_output(open_port_command, shell=True)
            else:
                print("Updating firewall rules...")
                subprocess.check_output(f"gcloud compute firewall-rules update firewall-rule --allow {tcp_ports},{udp_ports}", shell=True)
                
            print("Ports successfully opened.")

    if (len(updated_settings["azure"]) > 0 or len(updated_settings["gcp"]) > 0):
        create_documentation_file(updated_settings)


def create_documentation_file(settings):
    print("Creating Documentation file...")

    date_time = datetime.datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
    
    os.rename("Azure.conf", f"Azure_{date_time}.conf")
    os.rename("GCP.conf", f"GCP_{date_time}.conf")

    print(".conf files renamed successfully.")
    
    with open(f"VMcreation_<{date_time}>.txt", "w") as f:
        f.write(
            f"Date Stamp: {date_time}\n")
        f.write(f"System Admin Name: {getpass.getuser()}\n\n")
        for setting in settings["azure"]:
            f.write(f"Name: {setting['name']}\n")
            f.write(f"Purpose: {setting['purpose']}\n")
            f.write(f"Team: {setting['team']}\n")
            f.write(f"OS: {setting['os']}\n")
            for key, val in setting.items():
                if key not in doc_params and key != "name":
                    f.write(f"{key}: {val}\n")
            status = subprocess.check_output(
                f"az vm show -g {setting['resource-group']} -n {setting['name']} --show-details --query powerState", shell=True)
            f.write(f"Status of the VM {status.decode('utf-8')}\n\n")
        for setting in settings["gcp"]:
            f.write(f"Name: {setting['name']}\n")
            f.write(f"Project: {setting['project']}\n")
            f.write(f"Purpose: {setting['purpose']}\n")
            f.write(f"Team: {setting['team']}\n")
            f.write(f"OS: {setting['os']}\n")
            for key, val in setting.items():
                if key not in doc_params and key != "name":
                    f.write(f"{key}: {val}\n")
            status = subprocess.check_output(
                f"gcloud compute instances describe {setting['name']} --zone={setting['zone']} --format='value(status)'", shell=True)
            f.write(f"Status of the VM {status.decode('utf-8')}\n")
    print("Documentation created successfully.")


def main():
    azure_ports = (
        input("Enter port numbers to open for Azure (separated by spaces or press enter for no ports): ").split(" "))
    gcp_ports = (
        input("Enter port numbers to open for GCP (separated by spaces or press enter for no ports): ").split(" "))

    settings = read_config("Azure.conf", "GCP.conf")

    if settings:
        execute_commands(settings, azure_ports, gcp_ports)
    
    print("Script completed execution.")


main()
