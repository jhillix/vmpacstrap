.. _customisation_hooks:

Developing live scripts and customisation hooks
===============================================

:file:`vmpacstrap` is available in git.

Calls to vmpacstrap are best scripted. See the README for notes
on which options and settings are required to make a live image using
vmpacstrap.

The 'common' library contains functions and parameters which need to
be used in *all* images, including::

 export_env
 mount_proc
 disable_daemons
 prepare_apt_source

 replace_apt_source
 remove_daemon_block
 cleanup

.. _cleanup:

cleanup
-------

Ensure that :file:`proc` is unmounted even if the customisation fails or else
the image build itself will fail to unmount :file:`${rootdir}`.

.. _export_env:

export_env
----------

Debconf needs to be set in noninteractive mode to prevent the image
build waiting for keyboard intervention.

.. _mount_proc:

mount_proc
----------

Many packages require ``/proc`` to be mounted inside the chroot during
installation - cleanup must be specified as a trap if ``mount_proc`` is
used::

 trap cleanup 0

.. _disable_daemons:

disable_daemons
---------------

Packages which include a daemon **must not** start those daemons inside
the chroot as this will make the ``${rootdir}`` appear busy and the unmount
will fail. All scripts need to use :ref:`remove_daemon_block` after package
installation is complete.

.. _prepare_apt_source:

prepare_apt_source
------------------

The final Arch mirror location is not useful during the build when there
is a faster mirror available during the build. This function moves the
specified mirror file aside and uses the nearby mirror. Always use with
:ref:`replace_apt_source`.

Ensure that the mirror and suite are passed as arguments to prepare_apt_source::

 prepare_apt_source http://mirror/debian jessie

.. _remove_daemon_block:

remove_daemon_block
-------------------

After using :ref:`disable_daemons`, a policy script remains which needs
to be removed to allow daemons to start normally when the image itself
is booted. Use ``remove_daemon_block`` as the next step once package
installation is complete.

.. _replace_apt_source:

replace_apt_source
------------------

Requires :ref:`prepare_apt_source` to have been run first, then undoes the
change to the apt sources and cleans up.

.. index: task

.. _task_packages:

TASK_PACKAGES
-------------

Some task packages are useful to all images, these are specified here
and should be included in the set of packages to be installed using
all customisation scripts.

.. index: extra

.. _extra_packages:

EXTRA_PACKAGES
--------------

Packages which are not part of an existing task but which are useful for
all images and should be included in the set of packages to be installed
using all customisation scripts.

.. _new_architectures:

New architectures
-----------------

The precursor to new architecture support is :file:`vmpacstrap` support. A
default :file:`vmpacstrap` (with no customisation hook) will need to work
and any changes to the settings (e.g. ``--no-kernel --package linux-myarch-flavour``)
There is default support for some architectures in :file:`vmpacstrap`
(e.g. armhf architectures select the armmp kernel), such support depends
on how many users would use the same kernel compared to the number of
possible kernel flavours for that architecture.

The package list also needs a review - some packages will simply not
exist for the specified architecture. Some architecture-specific packages
need to be added, so each architecture has a particular customisation
hook script. Package names frequently change between releases, so the
package selection needs to be suite specific as well.
