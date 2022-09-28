Common Works Registration Exports
=======================================

`Common Works Registration (CWR) <https://matijakolaric.com/articles/1/>`_ 
is a protocol and a file format for batch registrations of musical works with collecting societies worldwide. Publishers send registrations and societies reply with acknowledgement files. Registrations in this formats are usually called CWRs and acknowledgement ACKs.

Unofficially, CWRs are also used for data exchange among publishers.

CWR is an extremely complex topic. Only technical aspects of creating CWR files and 
:doc:`importing acknowledgements <manual_ackimport>` are covered in this manual.

.. note::
    Collecting societies and other receivers of CWR files may, if issues arise, refer you to the software **vendor** for support. 
    According to the :doc:`MIT license <LICENSE>`, that is you, not the **creator** of this software.


Add View
+++++++++++++++++++++

.. figure:: /images/add_cwr.png
   :width: 100%

   Add CWR export view

.. note::
    If *CWR delivery code* is not entered as ``PUBLISHER_CODE`` in :ref:`settings`, ``000`` will be
    used. Such CWR files will not be accepted by most CMOs, but may be accepted by (sub-)publishers.

.. warning::
    Do NOT use an arbitratry CWR delivery code for creating CWR exports.

There are several ways to get to ``Add CWR Export`` view:

* by clicking ``Add CWR Export`` button or
* by using ``Create CWR from selected works`` batch action in :doc:`manual_work`.

There are only three fields:

* ``CWR version/type`` is where you select the version of CWR and transaction type. Here are current options: 

  * CWR 2.1: New work registrations
  * CWR 2.1: Revisions of registered works
  * CWR 2.2: New work registrations
  * CWR 2.2: Revisions of registered works
  * CWR 3.0: Work registration
  * CWR 3.0: ISWC request (EDI)
  * CWR 3.1 DRAFT: Work registration

.. note::
    Consult with the receiver which version they can process. If they can process multiple versions, choose the 
    highest.

* ``Internal note`` is a field where you can put a meaningful description of the export. 

.. warning::
    File naming is part of the CWR specifications. CWR file names should NOT be changed.
    
* ``Works`` is a multi-select field for works to be included in CWR exports.

CWR Export model does not have ``change view``, nor ``delete`` button. CWR files once created should
NOT be deleted, although they may not be used. Use `internal note` to mark a CWR file as not sent.

List View
+++++++++++++++++++++

.. figure:: /images/cwr_list.png
   :width: 100%

   List CWR export view

``CWR export list`` view. Besides the link in the first column with the file name, which
opens a view with additional information, and the counter that opens the list of works in this file,
it has two additional links in each row: ``View CWR`` and ``Download``.

The latter downloads the zipped CWR file, and the former opens the CWR file for viewing.

View CWR
--------------------

.. figure:: /images/highlight.png
   :width: 100%

   CWR 2.1 NWR (work registration) file with basic syntax highlighting

The example shown above shows the CWR file with basic syntax highlighting. When you hover over the 
fields with your cursor, additional information is shown.
