from flask import Flask, render_template, request, jsonify
import json
import psycopg2
import psycopg2.errorcodes
import time
import logging
import random


app = Flask(__name__)
app.config["files"] = "."

global data_seats

data_seats ={
"1A":"available","1B":"available","1C":"available","1D":"available","1E":"available","1F":"available",
"2A":"available","2B":"available","2C":"available","2D":"available","2E":"available","2F":"available",
"3A":"available","3B":"available","3C":"available","3D":"available","3E":"available","3F":"available",
"4A":"available","4B":"available","4C":"available","4D":"available","4E":"available","4F":"available",
"5A":"available","5B":"available","5C":"available","5D":"available","5E":"available","5F":"available",
"6A":"available","6B":"available","6C":"available","6D":"available","6E":"available","6F":"available",
"7A":"available","7B":"available","7C":"available","7D":"available","7E":"available","7F":"available",
"8A":"available","8B":"available","8C":"available","8D":"available","8E":"available","8F":"available",
"9A":"available","9B":"available","9C":"available","9D":"available","9E":"available","9F":"available",
"10A":"available","10B":"available","10C":"available","10D":"available","10E":"available","10F":"available"
}


@app.route("/")
def home():
	return render_template("UI.html")

@app.route("/create")
def create_table():
	conn = psycopg2.connect(database="hippo", user="hippo", password="datalake", host="127.0.0.1", port="5432")
	for k,v in data_seats.items():
		insert_seats(k, v, conn)
	conn.close()
	return "<h1>Table Created, click <a href='http://localhost:5000'>here</a> to open the app</h1>"

def insert_seats(seat_no, status, conn):
	with conn.cursor() as cur:
		cur.execute('CREATE TABLE IF NOT EXISTS userdetails (phone_no VARCHAR PRIMARY KEY, name VARCHAR, seats VARCHAR)')
		cur.execute('CREATE TABLE IF NOT EXISTS screen (seat_no VARCHAR PRIMARY KEY, status VARCHAR)')
		cur.execute("INSERT INTO screen (seat_no, status) VALUES (%s,%s)", (seat_no, status))
		logging.debug("insert_seats(): status message: {}".format(cur.statusmessage))
	conn.commit()

@app.route("/update", methods=['GET', 'POST'])
def update_seats():
	name = ''
	number = ''
	seats = []
	if request.method == 'POST':
		x = json.loads(request.form['data_seats'])
		user_data = json.loads(request.form['userdetails'])
		print(type(x))
		name = user_data['name']
		number = user_data['number']
		for k,v in x.items():
			if v == "reserved":
				seats.append(k)
				x[k] = "blocked"
		print(name)
		print(number)
		print(seats)
		seats_string = ','.join(seats)
		#print(x)
		conn = psycopg2.connect(database="cpdemo", user="hippo", password="datalake", host="127.0.0.1", port="5432")
		update(seats,conn)
		with conn.cursor() as cur:
			cur.execute("INSERT INTO userdetails (phone_no, name, seats) VALUES (%s,%s,%s)", (number,name,seats_string))
			logging.debug("insert_seats(): status message: {}".format(cur.statusmessage))
		conn.commit()
		conn.close()
	return json.dumps({"flag":0})

def update(seats,conn):
	for i in seats:
		print(type(i))
		with conn.cursor() as cur:
			cur.execute("UPDATE screen SET status = %s WHERE seat_no = %s",("blocked",i,))
			print("update_book_details(): status message: {}".format(cur.statusmessage))
		conn.commit()

@app.route("/getUsersDetails")
def usersDetails():
    temp = {}
    arr = []
    conn = psycopg2.connect(database="cpdemo", user="hippo", password="datalake", host="127.0.0.1", port="5432")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM userdetails")
        rows = cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        temp = {
            "phone_no": row[0],
            "name": row[1],
            "seats": row[2]
        }
        arr.append(temp)
    return json.dumps(arr)

@app.route("/details")
def details():
	return render_template("Seats.html")

@app.route("/get")
def staus():
	data_new={}
	conn = psycopg2.connect(database="cpdemo", user="hippo", password="datalake", host="127.0.0.1", port="5432")
	with conn.cursor() as cur:
		cur.execute("SELECT * FROM screen")
		logging.debug("print_balances(): status message: {}".format(cur.statusmessage))
		rows = cur.fetchall()
	conn.commit()
	for row in rows:
		data_new[row[0]]=row[1]
	conn.close()
	x = json.dumps(data_new)
	return x

    


if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)

