#!flask/bin/python
from flask import Flask, jsonify, request
import json
import collections
import MySQLdb
import datetime
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('config.properties')
hostname = config.get('DB','hostname')
username = config.get('DB','username')
password = config.get('DB','password')
database = config.get('DB','database')

db = MySQLdb.connect(hostname, username, password, database)
cursor = db.cursor()

app = Flask(__name__)

@app.route('/homeauto/api/1.0/switches', methods=['GET'])
def get_switches():
    cursor.execute("""
            Select id, name, description, status, last_changed, changed_by from switch
            """)
    rows = cursor.fetchall()
 
    # Convert query to row arrays
 
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        print row
        d['id'] = row[0]
        d['name'] = row[1]
        d['description'] = row[2]
        d['status'] = row[3]
        d['last_changed'] = row[4]
        d['changed_by'] = row[5]
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

@app.route('/homeauto/api/1.0/switches/<int:switch_id>', methods=['GET'])
def get_switch(switch_id):
    try:
	cursor.execute("Select * from switch where id=%s", (switch_id))
	rows = cursor.fetchall()
    except MySQLdb.Error, e:
        print "error: %s" % str(e)
	# Convert query to row arrays
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['name'] = row[1]
        d['description'] = row[2]
        d['status'] = row[3]
        d['last_changed'] = row[4]
        d['changed_by'] = row[5]
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

@app.route('/homeauto/api/1.0/switches', methods=['POST'])
def add_switch():
        if not request.json or not 'name' in request.json:
            abort(400)
        j = request.json
        name = j["name"]
        if 'description' in j:
            desc = j["description"]
        else:
            desc = ""
        if 'status' in j:
            status = j["status"]
        else:
            status = 0
        try:
            now = datetime.datetime.now()
            cursor.execute("""insert into switch (name, description, status, last_changed, changed_by)
                           values (%s,%s,%s,%s,%s)""",
                           (name, desc, status, now.strftime('%Y-%m-%d %H:%M:%S'),"naren"))
            db.commit()
            id = cursor.lastrowid
            return jsonify({'successfully added switch': id}),200
        except MySQLdb.Error, e:
            db.rollback()
            print "error: %s" % str(e)
            return jsonify({'Failed to add switch': ''}), 500

@app.route('/homeauto/api/1.0/switches/<int:switch_id>', methods=['PUT'])
def edit_switch(switch_id):
        if not request.json or not 'name' in request.json:
            abort(400)
        cursor.execute("Select name, description, status from switch where id=%s", (switch_id))
        rows = cursor.fetchall()
        if len(rows) == 0:
            return jsonify({'Switch ID does not exist': ''})
        orig = json.dumps(rows[0])
        req = request.json
        name = orig[1]
        desc = orig[2]
        status = orig[3]
        if 'name' in req:
            name = req["name"]
        if 'description' in req:
            desc = req["description"]
        if 'status' in req:
            status = req["status"]
        try:
            now = datetime.datetime.now()
            cursor.execute("""update switch set
                                name=%s, description=%s, status=%s, last_changed=%s, changed_by=%s where id=%s""",
                           (name, desc, status, now.strftime('%Y-%m-%d %H:%M:%S'), "naren",switch_id))
            db.commit()
            id = cursor.lastrowid
            return jsonify({'successfully added switch': id}),200
        except MySQLdb.Error, e:
            db.rollback()
            print "error: %s" % str(e)
            return jsonify({'Failed to add switch': ''}), 500

@app.route('/homeauto/api/1.0/switches/<int:switch_id>', methods=['DELETE'])
def delete_switch(switch_id):
        cursor.execute("delete from switch where id=%s", (switch_id))
        db.commit()
        return jsonify({'successfully deleted switch with ID': switch_id}),200
        
if __name__ == '__main__':
    app.run(debug=True)
