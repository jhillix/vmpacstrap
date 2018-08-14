README for vmpacstrap
========================

`pacstrap` installs a basic Arch system into a new root directory, for use
with `chroot`(8). `vmpacstrap` is a wrapper around it to install
Arch into a disk image, which can be used with virtual machines or
real hardware.

Refer to `pacstrap`s [source](https://git.archlinux.org/arch-install-scripts.git/tree/pacstrap.in) for more information.

Limitations
-----------

`vmpacstrap` is aimed principally at creating virtual machines, not
installers or prebuilt installation images. It is possible to create
prebuilt installation images for some devices but this depends on the
specific device. (A 'prebuilt installation image' is a single image file
which can be written to physical media in a single operation and which
allows the device to boot directly into a fully installed system - in a
similar way to how a virtual machine would behave.)

* `vmpacstrap` assumes that all operations take place on a local image
   file, not a physical block device / removable media.
* `vmpacstrap` is intended to be used with tools like `qemu` on the
   command line to launch a new virtual machine. Not all devices have
   virtualisation support in hardware.

This has implications for `u-boot` support in some cases. If the device
can support reading the bootloader from a known partition, like the
Beaglebone-black, then `vmpacstrap` can provide space for the bootloader
and the image will work as a prebuilt installation image. If the device
expects that the bootloader exists at a specific offset and therefore
requires that the bootloader is written as an image not as a binary which
can be copied into an existing partition, `vmpacstrap` is unable to
include that bootloader image into the virtual machine image.

It is possible to wrap `vmpacstrap` in such a way as to prepare a
*physical block device* with a bootloader image and then deploy the
bootstrap on top. However, this does require physical media to be
inserted and removed each time the wrapper is executed. Once you have
working media, an image can be created using ``dd`` to read back from
the media to an image file, allowing other media to be written with a
single image file. To do this, use the `--tarball` option to `vmpacstrap`
instead of the `--image`` option. Then setup the physical media and
bootloader image as required for the device, redefine the partitions to
make space for the rootfs, create a filesystem on the physical media and
unpack the `vmpacstrap` tarball onto that filesystem.

What you need
-------------

In order to use vmpacstrap, you'll need a few things:

* Arch Linux host - x86* or ARM
* pacstrap
* archlinuxarm-keyring
* extlinux
* qemu-img (in the qemu-utils package in Arch)
* parted
* mbr
* kpartx
* python-cliapp (see http://liw.fi/cliapp/)
* python jinja2

Testing vmpacstrap from git
------------------------------

There is a strongly recommended git pre-commit hook available
for vmpacstrap development - it requires the ``cmdtest``
package::

 ln -s ../../pre-commit.sh .git/hooks/pre-commit

Running vmpacstrap from git
------------------------------

$ sudo PYTHONPATH=. ./bin/vmpacstrap

vmpacstrap modules
---------------------

The single vmpacstrap script has been refactored to be the top
level settings parser and validator and the point where the other
modules (handlers) get to be called in a collaborative sequence.

The new modules are an attempt to work with a DRY process as well
as keeping the source code itself maintainable. Handler functions
need to check settings at the start so that calls to the handlers
can be retained in a simple flow. Where a function needs code from
multiple handlers, that function needs to be in the vmpacstrap
script but these should, ideally, be single calls into dedicated
calls from the relevant handlers which can return True|False or
raise cliapp.AppException to affect subsequent flow. Handlers must
NOT hook into other handlers, except Base or constants, only the
vmpacstrap script has the full set, so use function arguments to
pass variables populated by different handlers. Wherever possible,
large sections of new functionality need to be added as new handlers.

pylint
------

When using pylint, the following option is advised:

 $ pylint --ignore-imports=y vmpacstrap

(Despite the name of the option, this only ignores imports when
computing similarities and various handlers will end up needing
similar imports, it makes no sense to complain about that.)

Apart from that, vmpacstrap uses pylint and contains comments to
disable certain pylint checks in certain areas. pylint compatibility
will make it easier to accept patches, just follow the existing pattern
of pylint usage. pylint is far from perfect but can be helpful.

Testing UEFI support
--------------------

There is EFI firmware available to use with QEMU when testing images
built using the UEFI support, but this software is in Arch non-free
due to patent concerns. If you choose to use it to test UEFI builds,
a secondary change is also needed to symlink the provided OVMF.fd to
the file required by QEMU: bios-256k.bin and then tell QEMU about the
location of this file with the -L option:

$ qemu-system-x86_64 -L /usr/share/ovmf/ -machine accel=kvm \
  -m 4096 -smp 2 -drive file=amd64.img,format=raw

Note the use of -drive file=<img>,format=raw which is needed for newer
versions of QEMU.

The vmextract helper
--------------------

Once the image is built, various files can be generated or modified
during the install operations and some of these files can be useful
when testing the image. One example is the initrd built by the process
of installing a Arch kernel. Rather than having to mount the image
and copy the files manually, the vmextract helper can do it for you,
without needing root privileges.

$ /usr/share/vmpacstrap/vmextract.py --verbose \
  --image bbb/bbb-debian-armmp.img --boot \
  --path /boot/initrd.img-3.14-2-armmp \
  --path /lib/arm-linux-gnueabihf/libresolv.so.2

This uses python-guestfs (a Recommended package for vmpacstrap) to
prepare a read-only version of the image - in this case with the /boot
partition also mounted - and copies files out into the current working
directory.

The integration test suite
--------------------------

To run the vmpacstrap integration test suite, you need the yarn
tool, which is part of cmdtest. See <http://liw.fi/cmdtest/> and the
cmdtest package in Arch. The command to run the tests is:

    sudo yarns/run-tests

You can skip the slow tests that actually build images, by setting the
`TESTS` variable:

    sudo yarns/run-tests --env TESTS=fast

To format the test suite document:
(needs pandoc installed)

    make -C yarns

Making a release
----------------

Release are best made with the bumper tool (http://liw.fi/bumper/),
or simulating that by hand:

* Update version number (`vmpacstrap/version.py`, `NEWS`,
  `debian/changelog`).
* Also update `NEWS` to to say version is released (with date).
* Commit, and tag the commit with `vmpacstrap-x.y` for version x.y.
* Update version number and `NEWS` again to say the version is
  `x.y+git`. This makes it clear when a version is from git and not
  frmo a release.
* Commit.

CI will then build and upload packages. CI is currently running on
Lars's home server.

Legalese
--------

`vmpacstrap` is based on the fnatastic work of Lars Wirzenius' `[vmdebootstrap]`(http://git.liw.fi/vmdebootstrap/).
http://git.liw.fi/vmdebootstrap/

Copyright 2011-2013,2016  Lars Wirzenius
Copyright 2012  Codethink Limited
Copyright 2013-2016  Neil Williams
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

