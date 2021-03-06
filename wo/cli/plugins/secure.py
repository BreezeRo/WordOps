import getpass
import random
import string

from cement.core import handler, hook
from cement.core.controller import CementBaseController, expose

from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVariables


def wo_secure_hook(app):
    pass


class WOSecureController(CementBaseController):
    class Meta:
        label = 'secure'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = ('Secure command secure auth, ip and port')
        arguments = [
            (['--auth'],
                dict(help='secure auth', action='store_true')),
            (['--port'],
                dict(help='secure port', action='store_true')),
            (['--ip'],
                dict(help='secure ip', action='store_true')),
            (['user_input'],
                dict(help='user input', nargs='?', default=None)),
            (['user_pass'],
                dict(help='user pass', nargs='?', default=None))]
        usage = "wo secure [options]"

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if pargs.auth:
            self.secure_auth()
        if pargs.port:
            self.secure_port()
        if pargs.ip:
            self.secure_ip()

    @expose(hide=True)
    def secure_auth(self):
        """This function secures authentication"""
        pargs = self.app.pargs
        passwd = ''.join([random.choice
                          (string.ascii_letters + string.digits)
                          for n in range(24)])
        if not pargs.user_input:
            username = input("Provide HTTP authentication user "
                             "name [{0}] :".format(WOVariables.wo_user))
            pargs.user_input = username
            if username == "":
                pargs.user_input = WOVariables.wo_user
        if not pargs.user_pass:
            password = getpass.getpass("Provide HTTP authentication "
                                       "password [{0}] :".format(passwd))
            pargs.user_pass = password
            if password == "":
                pargs.user_pass = passwd
        Log.debug(self, "printf username:"
                  "$(openssl passwd -crypt "
                  "password 2> /dev/null)\n\""
                  "> /etc/nginx/htpasswd-wo 2>/dev/null")
        WOShellExec.cmd_exec(self, "printf \"{username}:"
                             "$(openssl passwd -crypt "
                             "{password} 2> /dev/null)\n\""
                             "> /etc/nginx/htpasswd-wo 2>/dev/null"
                             .format(username=pargs.user_input,
                                     password=pargs.user_pass),
                             log=False)
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure auth into Git")

    @expose(hide=True)
    def secure_port(self):
        """This function Secures port"""
        pargs = self.app.pargs
        if pargs.user_input:
            while not pargs.user_input.isdigit():
                Log.info(self, "Please enter a valid port number ")
                pargs.user_input = input("WordOps "
                                         "admin port [22222]:")
        if not pargs.user_input:
            port = input("WordOps admin port [22222]:")
            if port == "":
                pargs.user_input = 22222
            while (not port.isdigit()) and (port != "") and (not port < 65556):
                Log.info(self, "Please Enter valid port number :")
                port = input("WordOps admin port [22222]:")
            pargs.user_input = port
        WOShellExec.cmd_exec(self, "sed -i \"s/listen.*/listen "
                             "{port} default_server ssl http2;/\" "
                             "/etc/nginx/sites-available/22222"
                             .format(port=pargs.user_input))
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure port into Git")
        if not WOService.reload_service(self, 'nginx'):
            Log.error(self, "service nginx reload failed. "
                      "check issues with `nginx -t` command")
        Log.info(self, "Successfully port changed {port}"
                 .format(port=pargs.user_input))

    @expose(hide=True)
    def secure_ip(self):
        """IP whitelisting"""
        pargs = self.app.pargs
        if not pargs.user_input:
            ip = input("Enter the comma separated IP addresses "
                       "to white list [127.0.0.1]:")
            pargs.user_input = ip
        try:
            user_ip = pargs.user_input.split(',')
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            user_ip = ['127.0.0.1']
        for ip_addr in user_ip:
            if not ("exist_ip_address "+ip_addr in open('/etc/nginx/common/'
                                                        'acl.conf').read()):
                WOShellExec.cmd_exec(self, "sed -i "
                                     "\"/deny/i allow {whitelist_address}\;\""
                                     " /etc/nginx/common/acl.conf"
                                     .format(whitelist_address=ip_addr))
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure ip into Git")

        Log.info(self, "Successfully added IP address in acl.conf file")


def load(app):
    handler.register(WOSecureController)
    hook.register('post_argument_parsing', wo_secure_hook)
