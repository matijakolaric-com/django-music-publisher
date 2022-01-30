Writers
=======

Add/Change View
---------------

.. figure:: /images/add_writer.png
   :width: 100%

   Add writer view

``Add`` and ``change`` views for writers have several fieldsets.

Name
++++

``Last name`` and ``first name`` fields in the first, quite self-explanatory.
Only last name is required.

IPI
+++

``IPI name #`` and ``IPI Base #`` in the second. If you are unfamiliar with these
identifiers, see `IPI name and base numbers <https://matijakolaric.com/articles/identifiers/ipi/>`_.

Societies
+++++++++

``Performance Rights Society`` in the third. In most cases, writers are only affiliated with
performance rights societies. Depending on :ref:`settings`, fields for mechanical and even sync
affiliation might be visible.

General Agreement
+++++++++++++++++

In the last group, we have three fields:

* ``General agreement`` to mark that there is an original general agreement with this writer. This means that this writer must be controlled in all works.
* ``Society-assigned agreement number`` for the original general agreement between you and this writer (required in some societies)
* ``Publisher fee`` is the fee kept by the publisher when royalties are paid and distributed.

.. note::
    ``Publisher fee`` is not used in registrations. It is used only for
    :doc:`royalty statement processing <manual_royaltycalculations>`.
    Details are explained in that section.

Public
+++++++++++++++++

.. note::
    This section is only visible if file uploads are configured.

This section has two fields:

* ``Image`` - for uploading an image of the writer
* ``Description`` - for public description

Internal
++++++++++++++++++

This section has only a single field ``Notes``. You can use it in any way you
like.

List View
---------

.. figure:: /images/writers.png
   :width: 100%

   List writers view

The last column is both a work counter and link to the list of :doc:`works <manual_work>` by this writer.

``Can be controlled`` column requires an explanation.

For writers who are controlled (whose works are published by you), more data is required
than for those who are not. This column shows if data is sufficient for the writer to be
marked as controlled.

Controlled writers without affiliation and/or IPI name number
-------------------------------------------------------------

In very rare cases, writers choose not to affiliate with any society
and even get an IPI name number. And consequently not getting paid.

If you control such a writer, you can still enter them. If they don't
have an IPI name number, you can enter ``00000000000``. If they are not
affiliated with any performance rights society, there is a ``NO SOCIETY``
option at the bottom of the list.

This has to be manually re-entered on *every* save of the writer form.
It is a feature, not a bug. In almost all cases, both IPI name number
and PR affiliations should be entered for controlled writers. Entering
edge case exceptions should not be simple.

Other writers
------------------------------------------

For writers you do not control, you should still provide as much data as possible.

.. note::
    Only if ALL writers are identified with their IPI numbers,
    the work can receive an
    `International Standard Musical Work Code (ISWC) <https://matijakolaric.com/articles/identifiers/iswc/>`_.

