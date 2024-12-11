# COTW Platform for hosting CTF challenges

## Install/Setup

Requires docker compose (i.e. docker community edition)

1. Configure docker-compose file with appropriate variables
2. Customize landing/src/index.html
3. Edit landing/src/assets/js/main.js to match your flag regex/format
4. Create two tables in MariaDB database 'scoreboard' called current and global

Current requires two columns: username varchar(255) and time TIMESTAMP


Global requires three columns: username varchar(255), points int, and time TIMESTAMP


(I have yet to automate this/create a SQL db file/script for initalization)

## Challenge creation
See CHALLENGES.md


Note: This public version was s together in about 30 minutes, I will gladly accept PR's
- UNB Cybersec Prez
