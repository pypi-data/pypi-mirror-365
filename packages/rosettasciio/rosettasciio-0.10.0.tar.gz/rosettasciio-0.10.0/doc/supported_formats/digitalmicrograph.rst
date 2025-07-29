.. _digitalmicrograph-format:

Gatan Digital Micrograph
------------------------

RosettaSciIO can read both ``.dm3`` and ``.dm4`` files, but the reading features
are not complete (and probably they will remain so, unless Gatan releases the
specifications of the format). That said, we understand that this is an
important feature and if loading a particular Digital Micrograph file fails for
you, please report it as an issue in the `issues tracker
<https://github.com/hyperspy/rosettasciio/issues>`_ to make us aware of the
problem.

Some of the tags in the DM-files are added to the metadata of the signal
object. This includes, microscope information and certain parameters for EELS,
EDS and CL signals.


.. warning::

    It has been reported that in some versions of Gatan Digital Micrograph,
    any binned data stores the _averages_ of the binned channels or pixels,
    rather than the _sum_, which would be required for proper statistical
    analysis. We therefore strongly recommend that all binning is performed
    using python, e.g. `HyperSpy <https://hyperspy.org>`_, where possible.

    See the original `bug report here <https://github.com/hyperspy/hyperspy/issues/1624>`_.


API functions
^^^^^^^^^^^^^

.. automodule:: rsciio.digitalmicrograph
   :members:
