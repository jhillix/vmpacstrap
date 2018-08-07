"""
  Wrapper for Extlinux support
"""
# -*- coding: utf-8 -*-
#
#  extlinux.py
#
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import time
import logging
import cliapp
from vmpacstrap.base import Base, runcmd

# pylint: disable=missing-docstring


class ExtLinux(Base):

    name = 'extlinux'

    def __init__(self):
        super(ExtLinux, self).__init__()

    def install_extlinux(self, rootdev, rootdir):
        if not os.path.exists("/usr/bin/extlinux"):
            self.message("extlinux not installed, skipping.")
            return
        self.message('Installing extlinux')

        def find(pattern):
            dirname = os.path.join(rootdir, 'boot')
            basenames = os.listdir(dirname)
            logging.debug('find: %s', basenames)
            for basename in basenames:
                if re.search(pattern, basename):
                    return os.path.join('boot', basename)
            raise cliapp.AppException('Cannot find match: %s' % pattern)

        try:
            kernel_image = find('vmlinuz-.*')
            initrd_image = find('initrd.img-.*')
        except cliapp.AppException as exc:
            self.message("Unable to find kernel. Not installing extlinux.")
            logging.debug("No kernel found. %s. Skipping install of extlinux.", exc)
            return

        out = runcmd(['blkid', '-c', '/dev/null', '-o', 'value',
                      '-s', 'UUID', rootdev])
        uuid = out.splitlines()[0].strip()

        conf = os.path.join(rootdir, 'extlinux.conf')
        logging.debug('configure extlinux %s', conf)
        kserial = 'console=ttyS0,115200' if self.settings['serial-console'] else ''
        extserial = 'serial 0 115200' if self.settings['serial-console'] else ''
        msg = '''
default linux
timeout 1

label linux
kernel %(kernel)s
append initrd=%(initrd)s root=UUID=%(uuid)s ro %(kserial)s
%(extserial)s
''' % {
            'kernel': kernel_image,  # pylint: disable=bad-continuation
            'initrd': initrd_image,  # pylint: disable=bad-continuation
            'uuid': uuid,  # pylint: disable=bad-continuation
            'kserial': kserial,  # pylint: disable=bad-continuation
            'extserial': extserial,  # pylint: disable=bad-continuation
        }  # pylint: disable=bad-continuation
        logging.debug("extlinux config:\n%s", msg)

        # python multiline string substitution is just ugly.
        # use an external file or live with the mangling, no point in
        # mangling the string to remove spaces just to keep it pretty in source.
        ext_f = open(conf, 'w')
        ext_f.write(msg)

    def run_extlinux_install(self, rootdir):
        if os.path.exists("/usr/bin/extlinux"):
            self.message('Running extlinux --install')
            runcmd(['extlinux', '--install', rootdir])
            runcmd(['sync'])
            time.sleep(2)
        else:
            msg = "extlinux enabled but /usr/bin/extlinux not found" \
                  " - please install the extlinux package."
            raise cliapp.AppException(msg)

    def install_mbr(self):
        if not self.settings['mbr'] or not self.settings['extlinux']:
            return
        if os.path.exists("/sbin/install-mbr"):
            self.message('Installing MBR')
            runcmd(['install-mbr', self.settings['image']])
        else:
            msg = "mbr enabled but /sbin/install-mbr not found" \
                  " - please install the mbr package."
            raise cliapp.AppException(msg)
