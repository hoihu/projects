# Docker image for ESPOpen toolchain

This docker images provide an easy way to install the ESPOpen toolchain used to cross-compile Code for the Xtensa 8266 architecture without messing around with existing installations (of other toolchains...)

For example 8266 boards see Adafruit's Huzzah Feather board and of course the great micropython webpage (www.micropython.org)

The build instructions for the dockerfiles were taken from the espopen website:
https://github.com/pfalcon/esp-open-sdk

The dockerfile automatically clones the microptython repository.

## How to use it
1. install docker on your host system: https://docs.docker.com/engine/installation/ 
2. checkout this repository and store it somewhere on your HDD (e.g. home/xxx/projects)
3. run `docker build -f Dockerfile.esp -t espopen .`
... this will take a few hours (!), continue with a long walk :)
at the end you'll have a docker image called `espopen` with everything setup (SDK and micropython checkout)

You can use it for example like this:
`docker run -it espopen`

that will open a bash shell with user `xtensa`. From there you can do the usual staff like `make`, `git pull origin` etc.

## Copy build files to host
The firmware files cannot be directly flashed to the board because the serial port is not accessible. So you have to copy them over to your host system:

Call your docker image with a volume:
`docker run -it -v <yourpath>:<containerpath> espopen`
where ``<yourpath>` is the path on your HDD that is shared (e.g.`/Users/martin`) and <containerpath> is the path within your container (e.g. `/share`)

Then on the bash commandline (within the image), copy the firmware files:
`cp firmware-combined.bin /share ` and you'll find them on your host system under `/Users/martin`

## Update and build Micropython
If you want to update micropython and build it you can do it interactive via bash, as explained above.

A shortcut is to use the build dockerfile. It is based on the espopen image and automatically pulls the newest uPy and builds it.
 
To installl it (assuming you have built the espopen image as explained above): `docker build -f Dockerfile.build -t espbuild .` (you only need to do that once)
 
Then to update and compile everything: `docker run espbuild`

From now on, if you want the latest and greatest micropython esp8266 image, just enter `docker run espbuild`  :))
 
 
 ## TCP/IP flashing
 If you want to flash your esp board over a local tcp connection (e.g if you are using docker), try:
 
 `python rfc2217_server.py -p 4554 -v /dev/cu.SLAB_USBtoUART`

 you should now see something like

`INFO:root:RFC 2217 TCP/IP to Serial redirector - type Ctrl-C / BREAK to quit`
`INFO:root:Serving serial port: /dev/cu.SLAB_USBtoUART`
`INFO:root:TCP/IP port: 4554`

now flash your esp device using
`python esptool.py --port rfc2217://localhost:4554 --baud 480000 write_flash --flash_size=8m 0 firmware-combined.bin`

 
 
