# About

This little Docker container will listen on port 5299 for TTN and Helium integrations, and send location data to a [Traccar](https://www.traccar.org/) server.  

## How to

### Docker

Clone this repo and then add this to your `docker-compose.yml` file:

```yaml
  ttn2traccar:
    build: https://github.com/itec78/ttn2traccar.git
    container_name: ttn2traccar  # optional
    ports:
      - 5299:5299 #Port change
    environment:
      - "TRACCAR_HOST=https://traccar.example.com" # optional, defaults to http://traccar:8082
      - "TRACCAR_OSMAND=http://traccar.example.com:5055"  # optional, defaults to http://[TRACCAR_HOST]:5055
      - "LOG_LEVEL=DEBUG"  # optional, defaults to INFO
    restart: unless-stopped
  ```
  
  * `TRACCAR_HOST` is your Traccar server's URI/URL. If run in the same docker-compose stack, name your Traccar service `traccar` and omit this env var.
  * `TRACCAR_OSMAND` is your Traccar server's Osmand protocol URL
  



### Traccar

Create a device with ID = DevEUI (Device EUI)

### TTN

Add payload formatter to decode location data (latitude, longitude, altitude, speed, course)

Add webhook integration, sending uplink message to http://foo.bar:5299 (replace with your server url)

### Helium

Add funcion to decode location data (latitude, longitude, altitude, speed, course)

Add an integration, method POST, endpoint URL http://foo.bar:5299 (replace with your server url)

Add a flow joining device, function and integration

