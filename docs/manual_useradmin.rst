User Administration
===================

This section is covering user administration.

.. note::
    If you don't have the permission to manage other users, you don't see
    the ``Authentication and Authorization`` Section.

.. warning::
    If you have deployed DMP to Heroku, the password you used for the
    superuser account was written in plain text to the config variables.
    It is strongly recommended that you change the password upon the
    first login.

.. warning::
    Superusers should not do everyday tasks. Create staff users.

You add users by pressing on ``+ add`` link for the ``users`` in
the ``Authentication and Authorization``. The following view is shown:

.. figure:: /images/dmp_add_user.png
   :width: 100%

   Add User view

Add a username and a password twice and press on ``Save and continue
editing``. Then, in the next view, add additional data.

.. figure:: /images/dmp_change_user.png
   :width: 100%

   Change User view

.. note::
    Passwords are not visible, and not saved in plaintext.
    To change a password for another user, use ``this form`` link.

``Staff status`` has to be set for all users of Django-Music-Publisher,
and they have to be assigned to an appropriate permission group. Two
permission groups are set during installation:

* ``Publishing staff`` gives all permissions required for everyday
  publishing work
* ``Publishing audit`` gives read-only permissions to all data in
  Music Publisher module

Select one of them and press on the icon that will move it to ``chosen groups``. Then you can press ``save``.

.. figure:: /images/dmp_users.png
   :width: 100%

   User list view

You will be taken to the ``user list`` view. All users are shown here. Just as the add and change views, list views are quite standard. They will be covered a bit later.

Now you can log out, and log in as the newly added staff user. The ``home view`` is a bit different, according to the assigned permissions.
