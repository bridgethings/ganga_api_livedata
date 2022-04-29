pip install flask
sudo cp -r /home/pi/swan/flaskApp/flaskApp.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable flaskApp.service
sudo systemctl start flaskApp.service
