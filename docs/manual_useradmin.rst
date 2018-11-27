User administration
===================

Generally, it is a bad idea for superusers to do everyday works. Even if you are just one person, you may want to create a "normal" user first.

We do it by pressing on ``+ Add`` link for the ``Users`` in the ``Authentication and Authorization``. The following view is shown:

.. figure:: /images/dmp_add_user.png
   :width: 100%

   Add User view

We add the username and the password twice and press on ``Save and continue editing``. Then, in the next view, we can add aditional data.

.. figure:: /images/dmp_change_user.png
   :width: 100%

   Change User view

Please note that the password is not visible, and if the superuser needs to change it for another user, use the ``thsi form`` link in the password field.

``Staff status`` has to be set for all users of Django Music Publisher, and they have to be assigned to an appropriate permission group. Two permission groups are set during installation:

* ``Publishing Staff`` gives all permissions required for everyday publishing work
* ``Publishing Audit`` gives read-only permessions to all the data  in Django Music Publisher

Select one of them and press on the icon that will move it to ``Chosen groups``. Then you can press ``Save``.

.. figure:: /images/dmp_users.png
   :width: 100%

   User list view

You will be taken to the User list view. All users are shown here. Just as the add and change views, list views are very standard. They will be covered a bit later.

You can log out now, and log in as the newly added user. The home screen is a bit dirrefent, according to the assigned permissions.
