
# User's Manual
# Django Music Publisher


This is User's Manual for Django Music Publisher app. It presumes that installation was successful and user has logged in.
It also presumes you have acquired the token for the CWR validation and generation service.

![](django-admin.png)

After logging in, the home view of the administration interface is shown. User administration is not covered.

Music Publisher app has several models, each has three views: list, add and change. We will start by adding a
new work. Click on the **Add** next to **Work**.

![](add-work.png)

The **add view** for works is shown. Please note that Work **change view** is exactly same, so it will not be described
separately, but this is not the case with some of the other models. It has six parts:

* Title and ISWC
* Alternate Titles
* Writers in Work
* First Recording of the Work
* Artists Performing Work
* Work Acknowledgements

For a minimal work registration, all we need to enter are the *title*, and one *writer in work* record. So, let us do that.
We will put ``MINIMAL WORK`` in the field ``title`` and then press on the ``+`` sign in the ``writer`` column of the first
˙`writer in work˙` row. A popup will appear (if it does not, one may need to allow popups explicitely).

![](controlled-writer.png)

We will fill the minimal data for a controlled writer. If this writer is controlled in all works, e.g., there is a general
agreement between the original publisher and this writer, check 'generally controlled'. If your society requires it, also
enter the ``society-assigned agreement number``. Your society will provide you with information on agreement registrations.
Press ``save`` and you will return to the work **add view**. Please fill out the rest of the row.

![](wiw.png)

There is another ``society-assigned agreement number`` field here. The former is for **general agreements**, and this one is
for **specific agreements**. If you fill out both, the specific (latter, this) one will be used. Press ``save``. You will
be taken to the work **list view**.

![](work_list.png)









