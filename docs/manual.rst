User Manual
###########

This manual is aimed at music publishing professionals. It explains how Django Music Publisher is used, but it does not explain how music publishing works.

This manual continues at the point where :ref:`StandaloneDeployment` ended, presuming that Django Music Publisher was installed, migrations performed, a superuser created, predefined permission groups added, and that Django Music Publisher is running.

Logging In
==========

.. figure:: /images/dmp_login.png
   :width: 100%

   Default log-in view

The first screen that appears is the log-in screen. The title shown is the publisher name, so it will be change when you puy your data into the settings.

Please log in with the credentials you provided for the superuser during the istallation.

Home View
=========

.. figure:: /images/dmp_home.png
   :width: 100%

   Home view for superusers

The home view will show up after a succesfull login, in this example, it is the view superusers see. Depending on permissions, other users will see only a subset of the options present here.

In the header, the left part shows the name of the (main) publisher, and the right has the name of the current user as well as links for changing the password and logging out. This header is present in all views.

We have two colums, the left one shows the list of apps and modules, with links to change and add views. The right one shows the last 10 actions of the current user. It is empty, as we have not done anything yet.

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

Music Publishing App
====================

.. figure:: /images/home.png
   :width: 100%

   Home view for staff users

``Music Publisher`` has several top-level models, and each model has several views. We will start with the most important model ``Work``. Here is a brief overview of the related views.

* ``Add`` - view for adding new works
* ``List`` - view listing the works, includes search, filtering and batch actions
* ``Change`` - view for changing the work, includes delete button
* ``History`` - view where changes to a work are shown

All top-level models have these views. They are also inter-connected, so you will mostly start with pressing on ``Works``, to access the ``Work list`` view, or you will star by clicking on ``+Add`` in the ``Works`` model. As the list is empty, lets star with adding a new musical work.

Adding, Changing and Deleting Musical Works
===========================================

.. figure:: /images/add_work.png
   :width: 100%

   Add work view

The view for adding and changing works is shown in the image above. It is the most complex view in Django Music Publisher. It has several parts, so let us cover them one by one.

General
+++++++

This part contains the fields ``Title`` and ``ISWC``, as well as read-only field ``Work ID``, which is set automatically upon first save. Please note that the label ``Title`` is bold, representing that this field is required. So, lets put a title in.

Alternate Titles
++++++++++++++++

This part is pretty self-explanatory. Press on ``Add another Alternate Title`` and put the title in the field. Please note the icon for deleting the row.

.. figure:: /images/alternate_title.png
   :width: 100%

Writers in Work
+++++++++++++++

This is where you put in the information on composers and lyricists who created this musical work. As information on at least one controlled writer is required, let us look at all the columns:

* ``Writer`` is where you can select a writer. The field is conditionally required for controlled writers, and at least one writer must be controlled, so you need to select at least one. But, as there are no writers, press on the green plus ``+`` sign next to it. A pop-up window appears. Fill out ``First name``, ``Last name``, ``IPI Name #`` and ``Performing Rights Society``, and press ``Save``. The newly added writer will appear in this field. There is another way to add writers, which will be covered later. Please also note that for shares you do nto controll, this field is not required. If left empty, it means that the writer is unknown.

.. figure:: /images/popup_add_writer.png
   :width: 100%

   Add writer pop-up view

* ``Capacity`` is where you select how this writer contributed to the work, the options are: ``Composer``, ``Lyricist`` and ``Composer and Lyricist``. This field is required for controlled writers. Please note that the current version of Django Music Publisher does not support work modifications.

* ``Relative share`` is where the relative share (writers' split) is put in. The sum of relative shares for each work must be 100%. So, just put ``100`` in the only ``Writer in Work`` line.

* ``Controlled`` is where you select if you control the writer or not. Select it for the only ``Writer in Work`` line.

* ``Original publisher`` is a read-only field showing which entity is the original publisher. This field only makes sense for us publishers with multiple entities. It can be disabled in the settings.

* ``Society-assigned agreement number`` is a field where society-assigned agreement numbers for **specific agreements** are entered. For **general agreements**. they are set when defining the ``Writers``. If both exist, the **specific** one is used. This field can also be disabled in settings, as it is only used (and even required) in some societies. It may also be set as required for controlled writers. It should not be filled for other writers.

* ``Publisher fee`` is the fee kept by the publisher, while the rest is forwarded to the writer. Please note that this is a preparation for the upcoming royalty statement processing feature. This field can also be disabled in the setttings. It may also be set as required for controlled writers. It should not be filled for other writers.

First Recording
+++++++++++++++

Django Music Publisher can only hold data on the first recording of a musical work, not all of them. This is caused by the fact that not all societies world-wide have removed the long obsolete rule in CWR. This may change in future releases.

.. figure:: /images/first_recording.png
   :width: 100%

   Data on the first recording of the work

All fields are self-explanatory. Please note that fields ``Album / Library CD`` and ``Recording Artist`` behave in the same way the described field ``Writer`` does. Let us presume that our first work has not been recorded yet and remove this form.

Artists Performing Works
++++++++++++++++++++++++

Here you list the artists who are performing the work, there is no need to repeat the ``Artist`` set as the ``Recording Artist`` in the previous section. Leave this empty for now.

Work Registrations
++++++++++++++++++

This is where the work registrations are recorded. Please note that only superusers (in the default configuration) can modify this section, as it is automatically filled out from uploaded acknowledgement files. This will be covered a bit later in this document.

Work list view
++++++++++++++

.. figure:: /images/work_list.png
   :width: 100%

   Work list view

Once you press ``Save``, you are taken to the ``Work list view``.