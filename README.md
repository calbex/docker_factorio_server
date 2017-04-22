## Requirements
- SSH key for the client must be setup in DigitalOcean
- Ansible

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
python digitalocean-setup.py create --domain example.com --ansible
```

This will create a new server at factorio-*****.net.example.com.

## Save and Destory
Once you are finished with the server you can download the saves files
and destory the server by running the following.
```
python digitalocean-setup.py delete --list --save
```

This assumes you have only run the above command once. If you want to run
mulitple servers it is recommended to have seperate clones of this repo.
The save file is saved as `saves.tar.gz` in the root of the git repo.
