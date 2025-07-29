=============
SELF DESTRUCT
=============

.. |---| unicode:: U+2014
           :trim:

.. image:: https://img.shields.io/pypi/v/self-destruct.svg?style=for-the-badge
   :target: https://pypi.org/project/self-destruct/

``self-destruct`` is a simple Python library for stopping and terminating EC2
instances from within themselves, which is not officially supported by AWS.
Usage is very simple:

.. code-block:: python

    from self_destruct import self_destruct

    self_destruct()

The only customization option is the specification of a parameter
``terminate: bool = True`` which allows the user to specify whether they want to
terminate the instance or merely stop it.

Note that in order for this function to be successful, the EC2 instance must
have the following permissions:

::

    "ec2:DescribeInstances"
    "ec2:StopInstances"
    "ec2:TerminateInstances"

Additionally, ``self-destruct`` can be run in module mode to ensure that the
instance is terminated when the Python script exits, regardless of whether any
errors are raised. To run as a module, use the following commandline syntax:

::

    python -m self_destruct [-o (stop | terminate)] (-m module | pyfile) [args ...]

When using ``-o``, any argument other than ``stop`` will result in instance
termination. This choice was made to ensure that a typo in the argument name
does not result in the instance failing to terminate.

^^^^^^^
WARNING
^^^^^^^

You are responsible for ensuring that your AWS instance terminates, and the
author of this package is not liable for any costs associated with the failure
of this package to actually terminate your instances.

In particular, this package cannot stop/terminate your instances if
``self_destruct()`` is never run |---| use module-mode to ensure that an uncaught
Python exception does not prevent ``self_destruct()`` from being called. There
is no protection from another program or the operating system killing the
program before ``self_destruct()`` can be called, even in module-mode, however.
It is your responsibility to ensure that this does not happen.
