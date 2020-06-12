User Administration
===================

This section is covering user administration. If you don't have the permission to manage other users, meaning you don't see the ``Authentication and Authorization`` module on your home screen, then just skip this section.

If you do, then *read this very carefully!*

First, if you have deployed DMP to Heroku, the password you used for the superuser account was written in plain text to the settings.
It is recommended that you change the password upon the first login.

Generally, it is a bad idea for superusers to do everyday tasks. Even if you are just one person, should create a "normal" user first.

We do it by pressing on ``+ add`` link for the ``users`` in the ``Authentication and Authorization``. The following view is shown:

.. figure:: /images/dmp_add_user.png
   :width: 100%

   Add User view

We add the username and the password twice and press on ``save and continue editing``. Then, in the next view, we can add additional data.

.. figure:: /images/dmp_change_user.png
   :width: 100%

   Change User view

Please note that the password is not visible, and if the superuser needs to change it for another user, use the ``this form`` link in the password field.

``Staff status`` has to be set for all users of Django-Music-Publisher, and they have to be assigned to an appropriate permission group. Two permission groups are set during installation:

* ``Publishing staff`` gives all permissions required for everyday publishing work
* ``Publishing audit`` gives read-only permissions to all the data in Music Publisher module

Select one of them and press on the icon that will move it to ``chosen groups``. Then you can press ``save``.

.. figure:: /images/dmp_users.png
   :width: 100%

   User list view

You will be taken to the ``user list`` view. All users are shown here. Just as the add and change views, list views are quite standard. They will be covered a bit later.

Now you can log out, and log in as the newly added user. The ``home view`` is a bit different, according to the assigned permissions.
