# About

This little Docker container will listen on port 5299 for TTN webhooks, and send location data to a [Traccar](https://www.traccar.org/) server.  

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
      - "LOG_LEVEL=DEBUG"  # optional, defaults to INFO
    restart: unless-stopped
  ```
  
  * `TRACCAR_HOST` is your Traccar server's URI/URL. If run in the same docker-compose stack, name your Traccar service `traccar` and omit this env var.




### Traccar

Create a device with ID = TTN End device ID (eui-xxxx...)

### TTN

Add payload formatter to decode location data (latitude, longitude, altitude, speed, course)

Add webhook integration, sending uplink message to your server http://foo.bar:5299

