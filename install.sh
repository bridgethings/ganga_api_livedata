pip install flask
sudo cp /home/pi/swan/flaskApp/flaskApp.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable flaskApp.service
