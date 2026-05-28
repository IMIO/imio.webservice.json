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

Testing the AMQP chain end-to-end
==================================

This section explains how to publish a test document through the full AMQP chain,
from the webservice to iA.Docs (server.dmsmail).

The supported document types are:

====  ===========  ===================================  ==============================
Code  Type         Description                          RabbitMQ exchange
====  ===========  ===================================  ==============================
0     COUR_E       Incoming mail (courrier entrant)      dms.incomingmail
1     COUR_S       Outgoing mail (courrier sortant)      dms.outgoingmail
2     COUR_S_GEN   Outgoing generated mail               dms.outgoinggeneratedmail
3     DELIB        Deliberation (signed)                  dms.deliberation
Z     EMAIL_E      Incoming email                        dms.incoming.email
====  ===========  ===================================  ==============================

Prerequisites
-------------

You need a working server.dmsmail checkout (e.g. in ``/srv/src/server.dmsmail/``)
with buildout already run **in ZEO mode**, and a Plone site created with the
example profile (so that documents with known ``scan_id`` values exist).

Enable ZEO mode
~~~~~~~~~~~~~~~~

Uncomment ``dev-zeo.cfg`` in ``buildout-main.cfg``:

.. code-block:: ini

   [buildout]
   extends =
       base.cfg
       port.cfg
       amqp.cfg
       dev.cfg
       dev-zeo.cfg
       test.cfg

Configure plone-path
~~~~~~~~~~~~~~~~~~~~~

In ``port.cfg``, set ``plone-path`` to the path of your Plone site object
(e.g. ``/Plone``, ``/3.1.x``). This value is used by ``amqp.cfg`` to set the
``site_id`` in the AMQP consuming server configuration. If it is wrong or empty,
the AMQP worker will fail to find the Plone site.

.. code-block:: ini

   [port]
   plone-path = /Plone

Re-run buildout
~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd /srv/src/server.dmsmail
   bin/buildout

This configures ``zeoserver``, ``instance1``, and ``instance-amqp`` as ZEO
clients with shared blobs, so they can run simultaneously against the same
database. Without ZEO mode, only one Zope instance can lock ``Data.fs`` at a
time.

1. Start infrastructure services
---------------------------------

.. code-block:: bash

   # PostgreSQL (port 5433) + PostgreSQL test (port 5432) + RabbitMQ (port 5672)
   cd /srv/src/imio.webservice.json
   docker compose -f docker-compose-dev.yaml up -d

2. Seed the database
--------------------

The ``file_type`` table must be populated. Connect to the postgres container and
check:

.. code-block:: bash

   docker compose -f docker-compose-dev.yaml exec postgres \
     psql -U user -d user -c "SELECT * FROM file_type;"

If the table is empty, run the init script:

.. code-block:: bash

   bin/init_db development.ini

Or insert the seed data manually:

.. code-block:: bash

   docker compose -f docker-compose-dev.yaml exec postgres \
     psql -U user -d user -c "
   INSERT INTO file_type (id, description) VALUES ('COUR_E', 'Courrier entrant');
   INSERT INTO file_type (id, description) VALUES ('COUR_S', 'Courrier sortant');
   INSERT INTO file_type (id, description) VALUES ('COUR_S_GEN', 'Courrier sortant Genere');
   INSERT INTO file_type (id, description) VALUES ('DELIB', 'Deliberation');
   INSERT INTO file_type (id, description) VALUES ('EMAIL_E', 'Email entrant');
   "

3. Start the webservice
-----------------------

.. code-block:: bash

   cd /srv/src/imio.webservice.json
   bin/pserve development.ini

The webservice runs on port 6543. The AMQP consumer in iA.Docs fetches the file
content back from this URL (configured as ``ws_url`` in ``zope.conf``), so it
must stay running.

4. Start iA.Docs (ZEO server + instances)
------------------------------------------

Start the ZEO server first, then the Zope instances:

.. code-block:: bash

   cd /srv/src/server.dmsmail

   # Start ZEO server
   bin/zeoserver fg

   # Start instance1 (web UI)
   bin/instance1 fg

   # Start the AMQP worker
   bin/instance-amqp fg

5. Start the document publisher and dispatcher
----------------------------------------------

.. code-block:: bash

   cd /srv/src/imio.webservice.json

   # Publishes File records from PostgreSQL to the RabbitMQ exchange
   bin/document_publisher development.ini

   # Start the dispatcher matching your document type:
   bin/incomingmail_dispatcher development.ini            # COUR_E
   bin/outgoingmail_dispatcher development.ini            # COUR_S
   bin/outgoinggeneratedmail_dispatcher development.ini   # COUR_S_GEN
   bin/deliberation_dispatcher development.ini            # DELIB
   bin/incoming_email_dispatcher development.ini          # EMAIL_E

6. Find a valid scan_id
-----------------------

For types that update existing documents (COUR_S, COUR_S_GEN, DELIB), the AMQP
consumer looks up an existing file by ``scan_id``. You must use a ``scan_id``
that already exists in the Plone catalog.

For types that create new documents (COUR_E, EMAIL_E), any new ``scan_id`` will
work.

If the example profile is loaded, you can list existing scan_ids:

.. code-block:: python

   # bin/instance-debug run
   site = app['3.1.x']
   catalog = site.portal_catalog
   for b in catalog(portal_type='dmsommainfile'):
       obj = b.getObject()
       print(obj.scan_id, b.getPath())

7. Submit the test document
---------------------------

Use the ``bin/webservice-test`` script:

.. code-block:: bash

   # Usage: bin/webservice-test <scan_type> <count> [counter] [update] [filename]
   # scan_type: 0=COUR_E, 1=COUR_S, 2=COUR_S_GEN, 3=DELIB, Z=EMAIL_E

Examples:

.. code-block:: bash

   cd /srv/src/imio.webservice.json

   # Incoming mail (new document, random scan_id)
   bin/webservice-test 0 1

   # Outgoing generated mail (update existing scan_id 012999900000018)
   bin/webservice-test 2 1 18 update test.odt

   # Incoming email
   bin/webservice-test Z 1

The script will:

1. POST metadata to ``/dms_metadata/{client_id}/{version}`` -- creates a ``File``
   record in PostgreSQL
2. Upload the file to ``/file_upload/{version}/{file_id}`` -- stores the file on
   disk and sets ``filepath``

Then ``document_publisher`` picks it up, publishes to the appropriate RabbitMQ
exchange, the dispatcher routes it to the per-client queue, and ``instance-amqp``
consumes it.

Message flow
------------

::

   webservice-test
       |  POST /dms_metadata + /file_upload
       v
   PostgreSQL (File record: type=<type>, amqp_status=false)
       |  polled by document_publisher
       v
   RabbitMQ exchange (e.g. "dms.incomingmail", "dms.outgoinggeneratedmail", ...)
       |  consumed by the matching dispatcher
       v
   RabbitMQ per-client queue (e.g. "dms.incomingmail.019999")
       |  consumed by instance-amqp (imio.zamqp.dms)
       v
   iA.Docs Plone site
       - Fetches file from webservice (GET /file/{client_id}/{external_id}/{version})
       - COUR_E: creates a new dmsincomingmail
       - EMAIL_E: creates a new dmsincoming_email (from .tar archive)
       - COUR_S, COUR_S_GEN, DELIB: finds existing document by scan_id, updates file

Troubleshooting
---------------

- **foreign key constraint on file_type**: the ``file_type`` table is empty,
  see step 2.
- **AttributeError: 'NoneType' object has no attribute 'get'** on
  ``acl_users``: ``plone-path`` is empty in ``port.cfg``, which results in an
  empty ``site_id`` in the AMQP configuration. Set ``plone-path`` to your Plone
  site path and re-run ``bin/buildout``, see prerequisites.
- **file not found (scan_id: ...)**: no file with that ``scan_id`` exists in the
  Plone catalog. Use a scan_id from an existing document, see step 6.
- **printf: invalid octal number**: you passed the full external_id as the
  counter argument to ``webservice-test``. Pass only the numeric counter
  (e.g. ``18`` not ``012999900000018``), see step 7.

Tests
=====

This package is tested using Travis CI. The current status of the add-on is :

.. image:: https://api.travis-ci.org/IMIO/imio.webservice.json.png
    :target: http://travis-ci.org/IMIO/imio.webservice.json
