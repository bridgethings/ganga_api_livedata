# API Implementation for displaying Sensor Data

Contains API for reading data from sensor.

### Service creation

create service with following setup to ensure api is running all time

```
Description=Gunicorn instance to serve myproject
After=network.target
[Service]
User=pi
WorkingDirectory=<path>
ExecStart= python <path>/app.py
Restart=always
[Install]
WantedBy=multi-user.target
```
