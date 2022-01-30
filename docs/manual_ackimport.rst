Importing CWR Acknowledgements
=====================================

Societies and administrative agencies (that handle CWR registrations for some societies) send CWR acknowledgement files in response to publishers' registrations.
They are also in CWR format. You may receive more than one CWR acknowledgement file for every CWR file you delivered.

.. note::
   **CWR acknowledgement file** means group of transactions of type **ACK** in a CWR file.
   **Work registration acknowledgement** means one of these transactions.

Django-Music-Publisher can import basic information from CWR acknowledgements sent in response to your CWR registrations:

* Date of the CWR acknowledgement file
* Sender of the CWR acknowledgement file
* Remote Work ID (work ID assigned by the sender of the CWR acknowledgement file)
* Status of the work registration
* ISWCs (optional)

Only CWR 2.1 acknowledgement files are fully supported, with an experimental support for CWR 3.0.

Add view
***************************

.. figure:: /images/add_ack.png
   :width: 100%

   Add view

This view only has two fields:

* ``Acknowledgement file`` is where you select the file from your file system
* ``Import ISWCs`` selects whether to import ISWCs or not.

Once you click on ``Save`` (any of them), the file is processed.

A brief report is created, with links to all works that received work acknowledgements, work titles and statuses.
It can also hold detailed information about encountered issues. All issues are also reported as messages.

.. note::
    Only works present in at least one of :doc:`CWR exports <manual_cwrexport>` are matched.

Actual work acknowledgements are shown in the last section of the ``change work view``, described *below*.

List view
*************************

List view is very simple and self-explanatory. Just as with ``CWR exports``, the file name is a link to a page with slightly more information, and the last one opens the CWR file with **syntax highlighting**. See :doc:`CWR exports <manual_cwrexport>` for more information.


Work registration acknowledgements
*************************************

.. figure:: /images/workack.png
   :width: 100%

   Work registration acknowledgement

They show the aforementioned information, with the exception of imported ISWCs, that go into the ISWC field at the top of the :doc:`change work view <manual_work>`. Column ``status`` is the most important one.

The registration process should end with ``Registration accepted``. 

``Registration accepted with changes`` is usually also OK. 

``Transaction accepted`` is sent by societies with a two-step process of importing CWR files. This means that the first step for this work was succesfull, and the second step is pending.

Any other status requires investigation. That is far beyond the scope of this user manual. Or any manual. Syntax highlighting of CWR acknowledgement files, mentioned above, may help in the process. Consult the official CWR documentation as well as inquiry with your society.

.. note::
    If you are instructed to contact the software **vendor**, according to the :doc:`MIT license <LICENSE>`, it is you, not the **creator** of this software.
