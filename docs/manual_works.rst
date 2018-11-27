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

Once you press ``Save``, you are taken to the ``Work list view``.