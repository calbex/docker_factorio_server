## Install
### DigitalOcean setup scripts
Requires python-digitalocean to be installed:
```
pip install -U python-digitalocean
```

### Run Docker Image 
```
./setup.sh
docker-compose build
docker-compose up -d
```

## Run
Create a new Factorio server on DigitalOcean:
```
python digitalocean-setup.py create --domain example.com
ansible-playbook -i factorio-*****.net.example.com, setup-factorio.yml
```

This will create a new server at factorio-*****.net.example.com.