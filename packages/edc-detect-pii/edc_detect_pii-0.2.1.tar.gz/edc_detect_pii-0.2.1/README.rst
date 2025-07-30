EDC Detect PII
--------------

.. code-block:: bash

    uv pip install edc-detect-pii

or just run the tool

.. code-block:: bash

    uv run edc_detect_pii.py <OPTIONS>

So far this just looks for names.

The default regex looks for any word in CAPS greater than two letters and may have spaces between words.

Two areas that are at risk of exposing PII are data migrations and jupyter notebooks.

To run on migration files, clone the repo and pass a local path. For example:

.. code-block:: bash

    uv run edc_detect_pii.py \
        --repo=/migrations \
        --exclude OTHER ABNORMAL NORMAL \
        --ext=py


To run on a jupyter notebook, pass a local path to a folder with notebooks

.. code-block:: bash

    uv run edc_detect_pii.py \
        --path=/my_notebooks \
        --exclude OTHER ABNORMAL NORMAL



todo
====
* allow custom regex and additional regex as arguments
* consider pre-commit hook that uses a config file of custom words to exclude
