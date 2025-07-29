Dataset adapters
================

Adapters can be used when a collection is derived from another one by
subsampling document and/or queries.

.. currentmodule:: xpmir.datasets.adapters

Adhoc datasets
--------------

.. autoxpmconfig:: RandomFold
    :members: folds

.. autoxpmconfig:: ConcatFold

Documents
---------

.. autoxpmconfig:: RetrieverBasedCollection

.. autoxpmconfig:: DocumentSubset

Assessments
-----------

.. autoxpmconfig:: AbstractAdhocAssessmentFold
.. autoxpmconfig:: AdhocAssessmentFold
.. autoxpmconfig:: IDAdhocAssessmentFold

Topics
------

.. autoxpmconfig:: AbstractTopicFold
.. autoxpmconfig:: TopicFold
.. autoxpmconfig:: IDTopicFold
.. autoxpmconfig:: TopicsFoldGenerator
.. autoxpmconfig:: MemoryTopicStore
.. autoxpmconfig:: TextStore
