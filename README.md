# The Idea: 
to have a single file server which can be placed in any folder and have the contents of the folder accessible across the internet

# The Approach:
Create a simple file server to serve/stream files using Flask (not optimal for production)
Create a Tunnel to a public domain (acheived using longtunnel) 

# How do i use it?
First install the pre-reqs:
* [Python](https://www.python.org/downloads/)
* [Node](https://nodejs.org/en/download)

# Install the following dependencies:
```pip install flask flask_compress```

```npm -g install longtunnel```

Download the LocaServe.py file, place it in the folder you want to serve and run the app

```python LocaServe.py```

the console will list the tunnel password and the public url generated for usage.

# Note:
Tested in windows and if you face any errors, try disabling firewall while you are enabling the server.
And once the app is exited, the sharing of the files also stops.
