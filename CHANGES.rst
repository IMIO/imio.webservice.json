Changelog
=========

0.9.0 (unreleased)
------------------

- Handle database disconnection for requests query and processing
  [mpeeters]

- Upgrade imio.dataexchange.core to 0.6.0
  [mpeeters]

- Implement basic auth for requests
  [mpeeters]

- Avoid to many connection error with PostgreSQL
  [mpeeters]

- Adapt the async request processes to be resilient to RabbitMQ restart
  [mpeeters]

- Adapt the document publisher to be resilient to RabbitMQ restart
  [mpeeters]

- Upgrade imio.amqp to 0.3.0 and imio.dataexchange.core to 0.5.0
  [mpeeters]

- Change logging for handler scripts
  [mpeeters]

- Upgrade imio.amqp to 0.2.2
  [mpeeters]

- Add a script to cleanup old uploaded files
  [mpeeters]

- Do not reimport data if only a new table need to be created during database initialization
  [mpeeters]

- Improve request query by reducing the number of queried columns
  [mpeeters]

- Upgrade imio.amqp to 0.2.1 and imio.dataexchange.db to 0.4.1
  [mpeeters]

- Upgrade imio.dataexchange.core to 0.4.0 and imio.dataexchange.db to 0.4.0
  [mpeeters]

- Refactor request views to delegate the logic to the request handler process
  [mpeeters]

- Ensure that the database is initialized if a table is missing
  [mpeeters]

- Fix deprecation warnings from the latest version of pyramid
  [mpeeters]

- ISI-47: Add `cache_duration` and `ignore_cache` parameters
  [mpeeters]

- ISI-41: Add the possibility to use query string for GET request
  [mpeeters]

- Handle separatly read and write requests
  [mpeeters]

- Implement an expiration and caching mecanism for requests and responses
  [mpeeters]

- Improve request_id generation to allow caching
  [mpeeters]

- Use HTTP response codes to differenciate the get_request endpoint responses
  [mpeeters]

- Upgrade imio.dataexchange.db to 0.3.2
  [mpeeters]

- Implement `EMAIL` document type
  [mpeeters]

- Add the `route_discovery` service that allow to get the applications for
  a given client
  [mpeeters]

- Return a message if the request is still in progress
  [mpeeters]

- Upgrade imio.dataexchange.core to 0.3.1
  [mpeeters]

- Add a process for messages in error
  [mpeeters]

- Add swagger service
  [mpeeters]

- Add the async process to handle requests
  [mpeeters]

- Implement the `router` service
  [mpeeters]

- Change the implementation for `request` service
  [mpeeters]

- Add `cornice_swagger` and `requests` to the package dependencies
  [mpeeters]

- Update to the latest version of pyramid
  [mpeeters]

- Add cornice to the dependencies
  [mpeeters]

- Add docker-compose files for development
  [mpeeters]

- Improve docker image
  [mpeeters]

- Initialize the database during pyramid startup
  [mpeeters]

- Improved webservice-test
  [sgeulette]

- Added possibility to pass filename as arg to webservice-test
  [gbastien]

- Added external_id info in validation error
  [sgeulette]

prod/0.8.0 (2017-06-13)
-----------------------

- Bump version
  [mpeeters]

- Update manifest and deb to include version and changelog files
  [mpeeters]


prod/0.7.1 (2017-06-13)
-----------------------

- Corrected md5. Added ricoh test scan_type
  [sgeulette]

- Start daemon-ogm
  [sgeulette]


prod/0.7 (2017-03-22)
---------------------

- Manage alphanumerical document type
  [sgeulette]

- Remove the document type code from client_id
  [mpeeters]

- Add scan_type parameter in webservice-test script.
  [sgeulette]

- Changed input dms_metadata schema to accept alphanumerical type.
  Added validator to check document_type (client_id) definition and added new error "INVALID_CLIENT_ID".
  [sgeulette]

prod/0.6 (2016-05-03)
---------------------

- Update the file route to add the version parameter
  [mpeeters]

- Update the document publisher
  [mpeeters]

- Get the document type from the external id
  [mpeeters]

- Make the type parameter optional
  [mpeeters]

- Add a validator to ensure that the external id contains the client id
  [mpeeters]

- Add a regexp to ensure that the external id contains 15 digits and a
  valid document type
  [mpeeters]

- Add version 1.2 for dms_metadata schema
  [mpeeters]

- Fix typo in wsresponse schema folder
  [mpeeters]

- Update the routing key of request messages
  [mpeeters]

- Add the application_id parameter to Request objects
  [mpeeters]

- Ensure that the routing key is unique for request messages
  [mpeeters]

- Update the request/response webservices names
  [mpeeters]


prod/0.5 (2015-04-22)
---------------------

- filemd5 is now required with dms_metadata 1.1
  [mpeeters]

- Add dms_metadata version 1.1
  [mpeeters]

- Avoid an error if the MD5 is in uppercase
  [mpeeters]

- Add logging for webservices requests and responses
  [mpeeters]

- Add the type_version parameter for requests
  [mpeeters]

- Move the views in separate modules
  [mpeeters]

- Order db row consumption
  [sgeulette]

- Improved webservice-test
  [sgeulette, mpeeters]

- Cache uploaded file md5
  [mpeeters]

- Validate file md5 with version 1.1
  [mpeeters]

- Refactor the file upload validation
  [mpeeters]


prod/0.4.3 (2014-11-25)
-----------------------

- Fix https for production
  [mpeeters]

- Get the latest version of the file
  [mpeeters]


prod/0.4.2 (2014-10-17)
-----------------------

- Remove the tag from the deb version
  [mpeeters]


prod/0.4.1 (2014-10-17)
-----------------------

- Fix the version in the Makefile
  [mpeeters]

- Added md5 entry in json schema
  [sgeulette]


prod/0.4 (2014-10-17)
---------------------

- Initial release
  [mpeeters]
