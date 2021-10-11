# Orienteering Race Video Overlay
This tool creates a beautiful, video-stabilised video of your orienteering race:
- Stabilises your video based on feature tracking
- Overlays a GPS track on a geo-referenced map file (orienteering map)
- Rotates the map according to your heading direction

## How to use it
The easiest way to use this tool is by using [Docker](https://en.wikipedia.org/wiki/Docker_(software)). After Docker is installed, it is as simple as running:

``` shell
docker run -p 8080:8080 jakobhaervig/orienteering-race-video-overlay
```

Then the web interface is available through a browser at: [`http://localhost:8080`](http://localhost:8080).

## Download and run source code
The script is written in Python..
