Musical Works: List View
========================

.. figure:: /images/work_list.png
   :width: 100%

   Work list view

The ``work list`` view, just as all other list views, has a ``search field``, an ``action bar``, a table with works and, once there are over 100 works in the database, pagination, all on the left side. On the right side, there is the ``add musical work`` button, which takes you to the appropriate view, and the set of ``filters``.

Filters change, based on the number of options. For four options or less, they are simple links, and for more, it turns into a pull-down menu,

Search works on titles, writer's last names, ISWCs, ISRCs (in related recordings) and work IDs (numeric part).

Data table can be sorted by almost any column, or combination of the columns, and counts are also links to :doc:`recording <manual_recordings>` and :doc:`CWR export <manual_cwr>` ``list`` views..

Exporting JSON
++++++++++++++++++++++++++

.. figure:: /images/work_list_action.png
   :width: 100%

   Exporting musical works in JSON format.

Select several (or all) works in the ``musical work list`` view, select the ``Export selected works JSON.`` or ``Export selected works JSON (normalized).`` action and press on ``Go``. A JSON file will be downloaded, containing all the information about your works.

The difference between these two formats is subtle and technical. Normalized data has no redundancy, so the file is smaller, but it is also more complicated to process.

If you ever choose to stop using Django Music Publisher and move on, there is no lock-in. While these JSON formats might be confusing, there are free on-line tools that will convert JSON to just about any other format you need. https://json-csv.com/ is the first one Google came up with.


CWR Exporting Wizard
++++++++++++++++++++

Currently the only other available action is to ``create CWR from selected works``. Once you run it, you will be taken to ``add CWR export`` view, described :doc:`here <manual_cwr>`.
