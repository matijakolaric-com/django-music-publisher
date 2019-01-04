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

All top-level models have these views. They are also inter-connected, so you will mostly start with pressing on ``Works``, to access the ``Work list`` view, or you will start by clicking on ``+Add`` in the ``Works`` model. As the list is empty, let us start with adding a new musical work.
