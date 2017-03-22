.. contents::

Error codes List
================

global errors
-------------

 - **INTERNAL_ERROR** : An internal error occured during the process of the request
 - **SCHEMA_VALIDATION_ERROR** : The JSON validation failed

schema webservice errors
------------------------

 - **UNKNOWN_SCHEMA** : The schema name or version is incorrect

file_upload webservice errors
-----------------------------

 - **MISSING_METADATA** : The metadata is not defined
 - **FILESIZE_MISMATCH** : The filesize does not match the filesize from the metadata
 - **MD5_MISMATCH** : The file MD5 does not match the MD5 from the metadata

dms_metadata webservice errors
------------------------------

 - **SCAN_DATE_INVALID** : The value for the field 'scan_date' is invalid
 - **SCAN_HOUR_INVALID** : The value for the field 'scan_hour' is invalid
 - **EXTERNAL_ID_DUPLICATE** : The value for the field 'external_id' already exist
 - **INVALID_EXTERNAL_ID** : The value for the field 'external_id' is invalid
 - **INVALID_CLIENT_ID** : The value for the field 'client_id' is invalid

Tests
=====

This package is tested using Travis CI. The current status of the add-on is :

.. image:: https://api.travis-ci.org/IMIO/imio.webservice.json.png
    :target: http://travis-ci.org/IMIO/imio.webservice.json
