cd /home/pi/swan

wget https://github.com/bridgethings/ganga_api_livedata/archive/refs/heads/main.zip

unzip ganga_api_livedata-main.zip

mkdir flaskApp

cp /home/pi/swan/ganga_api_livedata-main/. /home/pi/swan/flaskApp

cd flaskApp

chmod +x install.sh

./install.sh
