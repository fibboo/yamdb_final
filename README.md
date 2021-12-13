![example workflow](https://github.com/fibboo/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

# yatube and yamdb merged
## About:
I merged two different projects to deploy them together on one server.<br>
Both are work with https. <br><br>
yatube you can visit here https://fibboo.space/ <br>
yamdb is avaliable here https://yamdb.fibboo.space/redoc/

### Requirements:
docker https://docs.docker.com/engine/install/ <br>
docker-compose https://docs.docker.com/compose/install/

### Как запустить проект:

Clone project and cd to infra
```
git clone git@github.com:fibboo/infra_sp2.git
```
Create .env file as in the template infra/.env.template <br>
Change first and second level domains in infra/nginx/default.conf to yours <br>
Don't forget to set up DNS with your domain registrar<br>
Copy infra/ folder to you server
```
scp -r infra/ user@your-server-ip:/home/user/
```
Login to your server, and run init-letsencrypt.sh. This script will get ssl for your domains
```
ssh user@your-server-ip
chmod +x init-letsencrypt.sh
sudo ./init-letsencrypt.sh
```
Push for magic to happen

### Thanks
Thank Phillip for his instruction on how to get ssl with nginx, Let’s Encrypt, certbot and Docker https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71 <br>
I https://github.com/mrts/docker-postgresql-multiple-databases to do multipl databases on postgres with Docker

### About me
You can read here https://fibboo.space/about/author/
