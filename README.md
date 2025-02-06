# KYC Validate

## Setup virtualenv 

For setting up env
#### Windows
```
pip install virtualenv     
python -m virtualenv env
. env/Scripts/activate
```

#### Linux
```
pip install virtualenv     
virtualenv -p python3 env 
source env/bin/activate  
```

## Install packages 

```
pip install flask flask_cors face_recognition opencv-python python-ffmpeg imageio[ffmpeg] Pillow


```


## Install ffmpeg
```
 sudo apt-get install ffmpeg
```




## Run the server 
```
python app.py
```

chown -R rsk:rsk public
sudo chmod -R 755 /var/www/nginx-default/

python3 -m pip install flask[async]
