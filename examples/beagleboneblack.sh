#!/bin/sh

set -e

user=`whoami`

sudo vmpacstrap \
 --owner ${user} --verbose \
 --mirror http://httpredir.debian.org/debian \
 --log beaglebone-black.log --log-level debug \
 --arch armhf \
 --foreign /usr/bin/qemu-arm-static \
 --enable-dhcp \
 --configure-apt \
 --no-extlinux \
 --package u-boot \
 --package dosfstools \
 --distribution sid \
 --serial-console-command "'/sbin/getty -L ttyO0 115200 vt100'" \
 --customize "beagleboneblack-customise.sh" \
 --bootsize 100mib --boottype vfat \
 "$@"
