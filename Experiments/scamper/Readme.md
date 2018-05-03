# Experiments with [scamper](http://www.caida.org/tools/measurement/scamper/) tool

## Installation

The tool is installed in userspace

```bash
tar xvzf scamper-cvs-20161204a.tar.gz
cd scamper-cvs-20161204a
./configure --prefix=/home/steger/.local
make
make install
export PATH=$PATH:/home/steger/.local/bin
export MANPATH=$MANPATH:/home/steger/.local/share/man
```

## The first trial

Compenents:

* server process
* client process
* actor and result consumer

### The server process

The server process opens a control port to the public network so that client processes can connect to it.
In the local filesystem socket files are created for each connected client processes, through which the client nodes can be instructed to run active measurements.

To enable IPv4 measurements and to serve via port 9999 run:

```bash
mkdir -p /tmp/scamper
sc_remoted -4 -P 9999 -U /tmp/scamper
```

### The client process

The client process needs root privileges. 

For now the server porcess is locally available.

```bash
scamper -R 127.0.0.1:9999
```

### The measurement logic (actor and consumer) 

The logic is running in the server node.
Lookup and select the client's socket in the socket folder `/tmp/scamper`

Run the example code provided by _Matthew Luckie_.

```bash
echo "trace -z 1.2.3.4 8.8.8.8" | \
  sc_attach -i '-' -R /tmp/scamper/127.0.0.1:53306 -o '-' | \
  sc_warts2json
```
