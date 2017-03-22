Changelog
=========

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
