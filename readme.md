Summary:
At first I wanted to make the messaging service work together with the fastapi endpoints, but quickly gave up on the idea.
Fastapi can be run in multiprocessor mode, and this creates an overhead to synchronize the sending service.

Both the endpoints and the distribution service run asynchronously. Also, the distribution service could be modified to run in multiprocessor mode (yes, this would require a synchronization mechanism, but it doesn't look impossible)

The messaging service is made to be reliable, and reasonably efficient.

And it provides a timeout for the mailing. When the mailing becomes relevant (it's time to start the mailing) the message creation process starts. It's likely that most of the messages that will be sent out as part of the newsletter will be sent out the moment it starts. 
However, at any time a new customer may come in or the restrictions of the mailing may change, taking on new customers, so the mailing should be checked until it is finished. However, there won't be many clients during the time the newsletter is running, so it's not efficient to keep checking for new clients. 
Therefore the newsletter gets a timeout if no clients are found in the next check. This way the performance and responsiveness of the service can be adjusted flexibly. Make it more responsive -- reduce the timeout and check time for new mailings. Make it more efficient -- increase timeout and check time for new mailings.


Installation


Clone repository 
```bash
git clone https://gitlab.com/Myortv/mailing.git  
```

Create virtual envirement
```bash
python -m venv env
```

Activate envirement
```bash
. env/bin/activate
```

Install dependendencies
```bash
pip install -r mailing/req.txt
```

You need to install Postgres somehow. Follow guides for your linux destribution or official guide
https://www.postgresql.org/docs/current/installation.html
Also arch wiki link:
https://wiki.archlinux.org/title/PostgreSQL

You also need to get Prometheus, but it is optional. Here an download link:
https://prometheus.io/download/ 



You need to specify your envirement variables to get things done. I leave file called env.sh in root of repo.

```sh
export POSTGRES_HOST='127.0.0.1'
export POSTGRES_USER='postgres'
export POSTGRES_PASSWORD='postgres'
export POSTGRES_DB='mailing'
export MAILING_SERVER_URL=''
export AUTHTOKEN=''
export LOGGING_FILE=''
```

If you fresh install postgres locally, you should not change next lines:

```sh
export postgres_host='127.0.0.1'
export postgres_user='postgres'
export postgres_password='postgres'
export postgres_db='mailing'
```

It is oauth0 dependency. Follow oauth0 guides to obtaing domain and audience.

```sh
export OAUTHDOMAIN=''
export OAUTHAUDIENCE=''
```

Add url to endpont recieve messages

```sh
export MAILING_SERVER_URL=''
```

JWT token from recieving message service

```sh
export AUTHTOKEN=''
```

Path to your logging file. It is must be file, not derictory

```sh
export LOGGING_FILE=''
```



And, last thing you need is create postgres database.
I leave database dump with schema, for fast cration of new database.

```sh
psql mailing < test-task/mailing.sql
```

Now, just run
```sh
python mailing/main_sheduler.py
```



Tasks done:
1. Tests. (they can be runned, but i make totally 0 tests, but pytest runs well)
5. Swagger 
7. Oauth0 integration
9. Exception handling
10. Prometheus-formatted data output
11. Additional buisness logic
12. Logging

