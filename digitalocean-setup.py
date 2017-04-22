from __future__ import print_function
import argparse
import random
import string
import sys
import os
import subprocess
import time
import json
from getpass import getpass
import digitalocean


def get_random_string(length=5):
    """
    Generates a random string of input length
    """
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def eprint(*args, **kwargs):
    """
    Print to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


def read_server_file():
    """
    Reads the contents of the server file and converts
    it to a dictionary.
    """
    try:
        with open("servers.json", "r") as server_file:
            try:
                data = json.load(server_file)
            except:
                data = []
            return data
    except IOError:
        return []


def save_dict_to_file(filename, dict_to_save):
    # Write contents to file
    with open(filename, "w+") as server_file:
        server_file.seek(0)
        json.dump(dict_to_save, server_file, sort_keys=True,
                  indent=4, separators=(',', ': '))
        server_file.truncate()


def save_server_to_file(object_output):
    """ Saves the server object as JSON to the servers file
        object_output should be a function
    """
    # Get contents, update, and write to file
    data = read_server_file()
    data.append(object_output())
    save_dict_to_file("servers.json", data)


def droplet_details(droplet):
    def droplet_details_func():
        items = ["id", "name", "memory", "vcpus",
                 "disk", "ip_address"]
        return dict((i, getattr(droplet, i)) for i in items)
    return droplet_details_func


class MachineSetup(object):

    def __init__(self, secret_token, domain):
        self.secret_token = secret_token
        self.domain = domain
        self.manager = digitalocean.Manager(token=secret_token)

    def check_region(self, region):
        """
        Returns True if input is a valid DO region
        """
        region_slugs = [x.slug for x in self.manager.get_all_regions()]
        return region in region_slugs

    def create_domain_name(self, name):
        """
        Generates a domain name as a subdomain
        """
        return ("%s.%s.%s" % (name, "net", self.domain)).lower()

    def create_new_server(self, name, tag_name=None):
        """
        Creates a new DigitalOcean droplet, adds SSH keys,
        and tags the image.
        """
        keys = self.manager.get_all_sshkeys()
        machine_name = self.create_domain_name(name)
        droplet = digitalocean.Droplet(token=self.secret_token,
                                       name=machine_name,
                                       region='sfo2',
                                       image='docker-16-04',
                                       size_slug='512mb',
                                       ssh_keys=keys,
                                       backups=False)
        eprint("Creating new droplet...")
        droplet.create()
        eprint("Waiting for creation to complete...")
        droplet.load()
        # Poll status till is active
        while droplet.status == "new":
            time.sleep(6)
            droplet.load()
            eprint(".")
        eprint("Done.")
        # Tag the droplet
        if tag_name:
            eprint("Tagging...")
            tag = digitalocean.Tag(name=tag_name, token=self.secret_token)
            tag.create()
            tag.load()
            tag.add_droplets(droplet)
        # Returns an actived and tagged droplet
        return droplet

    def setup_domain_for_droplet(self, droplet, name):
        """
        Creates a DNS record to match the droplet hostname
        """
        domain = self.manager.get_domain(self.domain)
        domain.load()
        droplet.load()
        domain.create_new_domain_record(type="A", name="%s.net" % name,
                                        data=droplet.ip_address)

    def add_local_ssh_key(self):
        """
        WARNING this function will not working unless path is updated
            comment out the return statement
        """
        return
        user_ssh_key = open('/home/<$user>/.ssh/id_rsa.pub').read()
        key = digitalocean.SSHKey(token=self.secret_token,
                                  name='machine-name',
                                  public_key=user_ssh_key)
        key.create()

    def destroy_machines_by_tag(self, tag_name):
        """
        Removes all droplets matching the input tag
        """
        for droplet in self.manager.get_all_droplets(tag_name=tag_name):
            eprint("Destroying %s" % droplet.name)
            droplet.destroy()

    def destroy_machine_by_id(self, droplet_id):
        droplet = self.manager.get_droplet(droplet_id)
        eprint("Destroying %s" % droplet.name)
        droplet.destroy()


class DigitalOceanSetup(object):

    @staticmethod
    def create_interface(domain=None):
        """
        Create the MachineSetup object after asking the user for the API token
        """
        secret_token = getpass(prompt="DigitalOcean API Token: ")
        interface = MachineSetup(secret_token, domain)
        return interface

    @staticmethod
    def setup_args_create(parser):
        """
        Register the CMD args for the create function
        """
        parser.add_argument("--domain", required=False)
        parser.add_argument("--ansible", required=False,
                            dest="ansible", action="store_true")
        return parser

    @staticmethod
    def create(args):
        # Get the domain name
        if args.domain:
            domain = args.domain
        else:
            domain = str(raw_input("Enter domain name: "))

        interface = DigitalOceanSetup.create_interface(domain)

        machine_name = ("%s-%s" % ("factorio", get_random_string(5))).lower()

        # Create a new droplet
        droplet = interface.create_new_server(machine_name, "factorio")
        interface.setup_domain_for_droplet(droplet, machine_name)
        # Output the IP address and hostname for the new droplet
        eprint(droplet.ip_address)
        final_domain = interface.create_domain_name(machine_name)
        # Save droplet details to file
        save_server_to_file(droplet_details(droplet))
        print(final_domain)
        # Run ansible playbook
        if args.ansible:
            seconds = 15
            # Waiting is quite important here as the SSH agent needs time to start
            eprint("Waiting {0} seconds for server to init...".format(seconds))
            time.sleep(seconds)
            eprint("Running Ansible...")
            os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
            process = subprocess.Popen(["ansible-playbook", "-i", final_domain + ",",
                                        "--private-key", "~/.ssh/id_rsa",
                                        "setup-factorio.yml"],
                                       stdout=subprocess.PIPE)
            out, _ = process.communicate()
            eprint(out)

    @staticmethod
    def setup_args_delete(parser):
        """
        Register arguments for delete command
        """
        parser.add_argument("--tag", required=False)
        parser.add_argument("--save", required=False,
                            dest="save", action="store_true")
        parser.add_argument("--list", required=False,
                            dest="delete_list", action="store_true")
        return parser

    @staticmethod
    def delete(args):
        """
        Run the delete function
        """
        if args.tag is not None:
            tag = str(args.tag)
            interface = DigitalOceanSetup.create_interface()
            # Delete everything matching the tag
            interface.destroy_machines_by_tag(tag)
        elif args.delete_list:
            server_list = read_server_file()
            if len(server_list) == 1:
                interface = DigitalOceanSetup.create_interface()
                droplet_details = server_list[0]
                # Download the save game from the server
                if args.save:
                    eprint("Running Ansible...")
                    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
                    process = subprocess.Popen(["ansible-playbook", "-i",
                                                droplet_details["name"] + ",",
                                                "--private-key", "~/.ssh/id_rsa",
                                                "save-factorio.yml"],
                                               stdout=subprocess.PIPE)
                    out, _ = process.communicate()
                    eprint(out)
                # Now destory the droplet
                interface.destroy_machine_by_id(droplet_details["id"])
                # Save empty list to file
                save_dict_to_file("servers.json", [])
            else:
                eprint("Too many or no items in server list.")
        else:
            eprint("Missing arguments.")


if __name__ == "__main__":
    # Create arg parsers
    parser = argparse.ArgumentParser(description="Setup a DigitalOcean server")
    subparsers = parser.add_subparsers(dest="command")
    # Setup sub commands arguments
    parser_create = subparsers.add_parser(
        'create', help="Create a new droplet")
    DigitalOceanSetup.setup_args_create(parser_create)
    parser_delete = subparsers.add_parser('delete', help="Delete a droplet")
    DigitalOceanSetup.setup_args_delete(parser_delete)
    # Parse the command line arguments
    args = parser.parse_args()
    if args.command == "create":
        DigitalOceanSetup.create(args)
    elif args.command == "delete":
        DigitalOceanSetup.delete(args)
