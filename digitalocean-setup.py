from __future__ import print_function
import digitalocean
import time
import random
import string
import sys


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

if __name__ == "__main__":
    secret_token = "digitaloceanapitoken"
    domain = "example.com"
    interface = MachineSetup(secret_token, domain)

    machine_name = ("%s-%s" % ("factorio", get_random_string(5))).lower()

    # Create a new droplet
    droplet = interface.create_new_server(machine_name, "testing")
    interface.setup_domain_for_droplet(droplet, machine_name)
    # Output the IP address and hostname for the new droplet
    print(droplet.ip_address)
    print(interface.create_domain_name(machine_name))

    # Delete everything created after testing
    # interface.destroy_machines_by_tag("testing")