Adding, Changing and Deleting Musical Works
===========================================

.. figure:: /images/add_work.png
   :width: 100%

   Add work view

The view for adding and changing works is shown in the image above. It is the most complex view in Django Music Publisher. It has several parts, so let us cover them one by one.

General
+++++++

This part contains the fields ``Title`` and ``ISWC``, as well as read-only field ``Work ID``, which is set automatically upon first save. Please note that the label ``Title`` is bold, representing that this field is required. So, lets put a title in.

If ``allow_modifications`` is set, two more fields are shown, ``original title`` and ``version type``, with only the former being editable. By filling out this field, the ``version type`` will be set to ``modification`` and a more complex set of validation rules will apply.

Alternate Titles
++++++++++++++++

This part is pretty self-explanatory. Press on ``Add another Alternate Title`` and put the title in the field. Please note the icon for deleting the row.

.. figure:: /images/alternate_title.png
   :width: 100%

Writers in Work
+++++++++++++++

This is where you put in the information on composers and lyricists who created this musical work. As information on at least one controlled writer is required, let us look at all the columns:

* ``Writer`` is where you can select a writer. The field is conditionally required for controlled writers, and at least one writer must be controlled, so you need to select at least one. But, as there are no writers, press on the green plus ``+`` sign next to it. A pop-up window appears. Fill out ``First name``, ``Last name``, ``IPI Name #`` and ``Performing Rights Society``, and press ``Save``. The newly added writer will appear in this field. There is another way to add writers, which will be covered later. Please also note that for shares you do not control, this field is not required. If left empty, it means that the writer is unknown.

.. figure:: /images/popup_add_writer.png
   :width: 100%

   Add writer pop-up view

* ``Capacity`` is where you select how this writer contributed to the work, the options are: ``Composer``, ``Lyricist`` and ``Composer and Lyricist``. This field is required for controlled writers. Please note that at least one of the writers should be a ``Composer`` or a ``Composer and Lyricist``. If modifications are allowed, further roles are present and a far more complex set of validation rules applies. At least two rows are required, one being (original) ``Composer`` or a ``Composer and Lyricist``, and one being ``Arranger``, ``Adaptor`` or ``Translator``.

* ``Relative share`` is where the relative share is put in. The sum of relative shares for each work must be 100%. This is how the writers split the shares **prior** to publishing. For controlled writers, 50% for performing rights, 100% for mechanical and 100% for sync, of ``relative share`` is transferred to the publisher (you). Please note that Django Music Publisher does not support different splits.

* ``Controlled`` is where you select whether you control the writer or not. Select it for at least one ``Writer in Work`` row.

* ``Original publisher`` is a read-only field showing which entity is the original publisher. This field only makes sense for the US publishers with multiple entities. It can be disabled in the settings. `DMP Guru <https://dmp.guru>`_ instances show this field only if the publisher has enities in multiple US PROs.

* ``Society-assigned agreement number`` is a field where society-assigned agreement numbers for **specific agreements** are entered. For **general agreements**, they are set when defining the ``Writers``. If both exist, the **specific** one is used. This field can also be disabled in settings, as it is only used in some societies. It may also be set as required for controlled writers. It should **not** be filled for other writers. `DMP Guru <https://dmp.guru>`_ does not show this field for affiliates of US PROs and HFA, shows for all other societies. For affiliates of societies that require this field, it is automatically set as required.

* ``Publisher fee`` is the fee kept by the publisher, while the rest is forwarded to the writer. **This field is not used in registrations.** It is used only for royalty statement processing. This field can also be disabled in the settings. It may also be set as required for controlled writers. It should not be filled for other writers. `DMP Guru <https://dmp.guru>`_ sets this field as required for controlled writers. If it is set as a part of a general agreement in ``Writers``, it does not have to be set in ``Writer in Work``. If it is set in both places, the one from ``Writer in Work`` has precedence.

Setting ``allow_multiple_ops`` enables the option to cover the case with multiple original publishers per writer. As stated in many places, the data on other publishers can not be entered. So, in case of multiple original publishers, one of which is you, enter two ``Writer in Work`` rows with the same ``Writer`` and ``Capacity``, one controlled (with your share) and one for the other publisher(s).

First Recording
+++++++++++++++

**Django Music Publisher can only hold data on the first recording/release of a musical work, not all of them.** This is caused by the fact that not all societies and well-known sub-publishers have removed a long obsolete limit in CWR to one recording per work. This will change in future releases.

.. figure:: /images/first_recording.png
   :width: 100%

   Data on the first recording of the work

All fields are self-explanatory. Please note that fields ``Album / Library CD`` and ``Recording Artist`` behave in the same way the described field ``Writer`` does. Let us presume that our first work has not been recorded yet and remove this form.

**Please read the part on ``Albums and/or Library CDs`` for details on albums and music libraries, as this is often a source of confusion for production music publishers.**

Artists Performing Works
++++++++++++++++++++++++

Here you list the artists who are performing the work, there is no need to repeat the ``Artist`` set as the ``Recording Artist`` in the previous section. 

Registration Acknowledgements
+++++++++++++++++++++++++++++++++++

This is where the work registration acknowledgements are recorded. Please note that only superusers (in the default configuration) can modify this section, as it is automatically filled out from uploaded acknowledgement files. This will be covered later in this document.

Once you press ``Save``, you are taken to the ``Work list view``.

