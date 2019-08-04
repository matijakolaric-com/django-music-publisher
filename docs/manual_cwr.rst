Creating CWR Export
===================

.. figure:: /images/add_cwr.png
   :width: 100%

   Add CWR export view

There are several ways to get to ``Add CWR Export`` view:

* from the ``home`` page or app menu or ``CWR Export list`` view by pressing on ``Add CWR Export`` button or
* from the ``Create CWR from selected works`` batch action in ``Work list`` view.

Please note that the field ``Works`` uses auto-complete, and if you don't come here through the action, you must add works in this view one at a time.

``CWR version/type`` field selects the CWR version and transaction type. CWR 2.1 makes a distinction between ``New Work Registrations`` and ``Revisions``, while CWR 3.0 (not yet in use anywhere) has no such distinction for registrations.

``Internal note`` is what the name says, you can enter whatever helps you to keep track. It can even be edited from the ``list`` view.

.. figure:: /images/cwr_list.png
   :width: 100%

   CWR export list view

Upon save, you will be taken to the ``CWR export list`` view. It has two links in each row: ``View CWR`` and ``Download``. The latter will download the zipped CWR file, and the former will take you to the preview:

Preview and Download
--------------------

.. figure:: /images/highlight.png
   :width: 100%

   CWR 3.0 WRK (work registration) preview with basic syntax highlighting

The example shown above shows the CWR file with basic syntax highlighting. When you hover over the fields with your cursor, additional information is shown.

.. figure:: /images/cwr_isr.png
   :width: 100%

   CWR 3.0 ISR (ISWC request) preview with basic syntax highlighting

CWR 3.0 introduces a new mechanisam for obtaining ISWCs. The short version is that publishers send ISWC requests (ISR), an example is shown here, and societies send answers (ISA).
Please note that CWR 3.0 support is still experimental.


CWR Delivery
------------

CWR Delivery is currently not implemented. CWR 2.1 manual delivery is a relatively simple task and CWR 3.0 is not accepted by any societies yet.
