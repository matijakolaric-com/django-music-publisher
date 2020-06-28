CWR Exports
===================

Common Works Registration (CWR) is a protocol and file format for batch registrations of musical works with collecting societies worldwide. Publishers send registrations and societies reply with acknowledgement files. Registrations in this formats are usually called CWRs and acknowledgement ACKs.

Unofficially, CWRs are also used for data exchange among publishers.

Add View
+++++++++++++++++++++

.. figure:: /images/add_cwr.png
   :width: 100%

   Add CWR export view

.. note::
    CWR exports can be created only if *CWR delivery code* is entered as ``PUBLISHER_CODE`` in :ref:`settings`.

.. warning::
    Do NOT use an arbitratry CWR delivery code for creating CWR exports. If you did, you should either start over 
    with a clean installation of DMP, or seek :doc:`professional support <support>`.
    
There are several ways to get to ``Add CWR Export`` view:

* by clicking ``Add CWR Export`` button or
* by using ``Create CWR from selected works`` batch action in :doc:`manual_work`.

There are only three fields:

* ``CWR version/type`` is where you select the version of CWR and transaction type. Here are current options: 

  * CWR 2.1: New work registrations
  * CWR 2.1: Revisions of registered works
  * CWR 3.0: Work registration (experimental)
  * CWR 3.0: ISWC request (experimental)

* ``Internal note`` is a field where you can put a meaningful description of the export. 

.. warning::
    File naming is part of the CWR specifications. CWR file names should NOT be changed.
    
* ``Works`` is a multi-select field for works to be included in CWR exports.

List View
+++++++++++++++++++++

.. figure:: /images/cwr_list.png
   :width: 100%

   CWR export list view

Upon save, you will be taken to the ``CWR export list`` view. It has two links in each row: ``View CWR`` and ``Download``. The latter will download the zipped CWR file, and the former will take you to the preview:

CWR Preview
--------------------

.. figure:: /images/highlight.png
   :width: 100%

   CWR 2.1 NWR (work registration) preview with basic syntax highlighting

The example shown above shows the CWR file with basic syntax highlighting. When you hover over the fields with your cursor, additional information is shown.
