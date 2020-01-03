Debugging
=========

1. Ensure that the request was correctly added to the database
--------------------------------------------------------------

- Enter into the postgres docker container : :code:`docker exec -ti webservicejson_postgres_1 bash`
- Connect to PostgreSQL database : :code:`sudo psql -U webservice`
- List the 5 latest requests : :code:`select * from request order by date desc limit 5`

2. Ensure that there is no pending message in RabbitMQ
------------------------------------------------------

- Connect to RabbitMQ through the web interface : :code:`http://server:15672`
- Verify the content of the queues :code:`ws.request.error` / :code:`ws.request.read` / :code:`ws.request.write` in the Queues tab.

3. Verify the queue consumers logs
----------------------------------

- For :code:`GET` requests : :code:`docker logs webservicejson_request_read_handler_1`
- For :code:`POST` requests : :code:`docker logs webservicejson_request_write_handler_1`
