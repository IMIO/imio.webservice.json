Debugging
=========

1. Ensure that the request was correctly added to the database
--------------------------------------------------------------

- Enter into the postgres docker container : `docker exec -ti webservicejson_postgres_1 bash`
- Connect to PostgreSQL database : `sudo psql -U webservice`
- List the 5 latest requests : `select * from request order by date desc limit 5`

2. Ensure that there is no pending message in RabbitMQ
------------------------------------------------------

- Connect to RabbitMQ throug the web interface : `http://server:15672`
- Verify the content of the queues `ws.request.error` / `ws.request.read` / `ws.request.write` in the Queues tab.

3. Verify the queue consumers logs
----------------------------------

- For `GET` requests : `docker logs webservicejson_request_read_handler_1`
- For `POST` requests : `docker logs webservicejson_request_write_handler_1`
