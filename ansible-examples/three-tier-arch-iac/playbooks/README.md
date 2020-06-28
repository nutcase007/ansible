## Nginx+MariaDB Deployment

- Requires Ansible 1.2 or newer
- Expects CentOS/RHEL 7.x host/s

To use, copy the `hosts.example` file to `hosts` and edit the `hosts` inventory 
file to include the names or URLs of the servers you want to deploy.

Then run the playbook, like this:

 ansible-playbook -i hosts site.yml

The playbook will install and configure MariaDB and Nginx.
