# Notebook project

#### Ty Dunn <tydunn@umich.edu>

1) Add a `credentials.py` that contains the values of everything imported in `check_in.py`

2) Install sqlite3 on your machine

3) Run `pip install -r requirements.txt`

4) Ensure that you accept inbound rules allow traffic on specified port and IP address

5) Ensure that the Twilio messaging webhook is pointed toward your url.

6) Run gunicorn -b localhost:8000 -w 2 -D notebook:app

7) Send `start` to the `to_num` to bootstrap the system
