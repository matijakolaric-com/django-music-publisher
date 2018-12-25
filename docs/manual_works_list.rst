Work List View
==============

.. figure:: /images/work_list.png
   :width: 100%

   Work list view

``Work list view``, just as all other list views, has a ``search field``, an ``action bar``, a table with works and, once there are over 100 works in the database, a pagination, all on the left side. On the right side, there is the ``Add Work`` button, which takes you to the appropriate view, and the set of ``filters``.

Save as new
+++++++++++

Before we do anything else, we need to get a few more works in. Usually, works come in batches where most of the information is the same, with only the title (and ISWC, if present) being changed. There is no need to repeat the whole process, just open the first work, change the title and press on ``Save as new`` button.

.. figure:: /images/save_as_new.png
   :width: 100%

   Save as new

Repeat the process several times, you may even add a few more writers, both controlled and not controlled. 

You may want to try using ``search field`` and ``filters``, the use should be pretty obvoius, so it will not be explained, search works on titles, including alternate ones, writer's last names, ISWCs and work IDs.

Exporting and creating CWR
++++++++++++++++++++++++++

Select several (or all) works in the ``work list view``, select the ``export selected works`` or ``export selected works (normalized)`` action and press on ``go``. A JSON file will be downloaded, containing all the information about your works. 

The difference between these two formats is subtle and technical. Normalized data has less redundancy, but it is also more complicated to process.

If you ever choose to stop using Django Music Publisher and move on, there is no lock-in. While the JSON format might be confusing, there re free online tools that will convert JSON to just about any other format you need. https://json-csv.com/ is the first one Google just came up with.

.. figure:: /images/export.png
   :width: 100%

   Exporting works.

Currently the only other available action is to ``create CWR from selected works``. Once you run it, you will be taken to ``add CWR export view``.