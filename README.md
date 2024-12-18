# Django Template

## Setup

Run the setup script to configure your project name and `.env` plus `docker-compose.override.yml` for local development.

```
./setup
```

This will setup your .env and docker-compose.override.yml file for local development.

```
docker-compose up -d
```

see logs
```
docker-compose logs
```

Shell into the python app container
```
docker-compose exec app /bin/bash
```

To make typing these commands less tedious it helps to have docker aliases in your .bash_profile or similar
```
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs'
```

Once in the app container you can run the django commands
```
python manage.py runserver 0.0.0.0:3000
``` 

# Deployment Instructions
## Deploying to Digital Ocean

To deploy to digital ocean you'll need doctl installed as a prerequisite.

On mac, `brew install doctl`

Then you'll need to config it with your digital ocean token. 

`doctl auth init`

In the deploy directory there are a number of scripts to help you get into production.  You run them from the parent directory.

* `deploy/go` will do everything
* `deploy/01-build-server` will make a digital ocean server and set `.digital_ocean_env` so your other scripts will work
* `deploy/02-config-server` this does everything to pave the road for deployment such as installing software and creating a non root user
* `deploy/03-deploy-repo` this will clone the repo in and copy up the env files mentioned below, then fire up docker compose 
* `deploy/userlogin` a shortcut for logging into the server
* `deploy/rootlogin` I should probably kill this
* `deploy/backup` take a copy of the production database
* `deploy/restore` restores the latest backup
* `deploy/cleanup` destroys the digital ocean server

If you are using the digital ocean deploy scripts in /deploy, there are two files you'll need;

* `.env-prod` for production configuration (same as .env unless you have different prod config)
* `.docker-compose-override.yml.prod` which open the app port

To setup completely new hosting, I purchased a domain from namecheap and configured custom dns pointing to digital ocean's nameservers - ns1.digitalocean.com, ns2.digitalocean.com, ns3.digitalocean.com (don't forgot to click the tick!).  I created a new project in digital ocean just to group the server and domain.  I added my new mac's public ssh key to my digital ocean team.   I think this key is used in two ways.  First to avoid needing to config doctl with a token and provide it all the time, automating the deployment script.  It is also added to the server by the deployment script for passwordless sign in.  I updated the .env-prod with domain name I purchased, and my ssh key name and public key.  I click-ops'd a dns domain/zone in digital ocean, but I think the deploy script does that. After that it was just a matter of running the deploy script.  You have to wait for dns propagation before certbot can get the challenge file.  