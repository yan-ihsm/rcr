# RCR - Resemble Chat Room

This project consists of 2 rcr types: server and client.

### Quick start

This project has no dependency on any thirdparty libraries.

To run the project, you can first start running the server:

```bash
$ ./bin/rcr -s
```

> -s stands for --server.

And then you can connect to the server by `telnet 127.0.0.1 9171`.

You can override config of the application by some environment variables:

```
SERVER_HOST
SERVER_PORT
CONNECTION_DRIVER
CONNECTION_PROTOCOL
LOG_LEVEL
```

You can find the list and default values in [`config.py`](./rcr/config.py) file.

For example to change the `SERVER_PORT` to something else:

```bash
$ SERVER_PORT=8090 ./bin/rcr -s
```

Also, if you want to connect client to the server, just run the previous command but without `-s` flag:

```bash
$ ./bin/rcr
```

### Commands

This prject supports these commands:

* `w`: get list of online clients.
* `msg <client id> <msg>`: to send a message to a specific client.
* `broadcast <str>`: to send a message to all clients.
* `url <client id> <url>`: to send a web page size to a specific client.
* `fib <client id> <n>`: to send a fibonacci's calculation to a specifc client.
