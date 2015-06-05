Changelog
=========

prod/0.5.1 (unreleased)
-----------------------

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
