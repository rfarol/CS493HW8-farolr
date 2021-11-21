from flask.templating import render_template_string
from google.cloud import datastore
from flask import Flask, request, jsonify, render_template_string
import json
import constants

# creation of location header was taken from: https://stackoverflow.com/questions/22669447/how-to-return-a-relative-uri-location-header-with-flask
# convert JSON object to HTML table was taken from: https://stackoverflow.com/questions/49390075/how-do-i-convert-python-json-into-a-html-table-in-flask-server/49391508

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

@app.route('/boats', methods=['POST','GET','DELETE'])
def boast_get_post():
    # post request 
    if request.method == 'POST':
        content = request.get_json()
        if content is None:
            # makes sure client sends supported MIME type
            return ('Please submit a JSON object', 415)
        else:    
            # search for all boats to find name constraint. 403 request 
            query = client.query(kind=constants.boats)
            list_boats = query.fetch()
            for boats in list_boats:
                if boats['name'] == content['name']:
                    return ("This boat already exists. Please add another one", 403)

            # check for invalid input types . 400 requests 
            if 'name' not in content.keys():
                return ('Please enter name', 400)
            if 'type' not in content.keys():
                return ('Please enter type', 400)
            if 'length' not in content.keys():
                return ('Please enter length', 400)

            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
            client.put(new_boat)
            boat = client.get(key=new_boat.key)
            boat['id'] = new_boat.key.id
            boat['self'] = request.url + "/" + str(new_boat.key.id) # add self URL
            return (boat, 201) # boat is returned as a JSON object. 201 request code 
        
    # get request for all boats 
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e["self"] = request.url + "/" + str(e.key.id) # add self URL 
            output = {"boat": results}
        return json.dumps(output)
    
        # delete request for all boats
    elif request.method == 'DELETE':
        return('Action not allowed', 405) # sets up safety net just in case someone deletes all boats
    
    else:
        # checks if client makes unsupported request to server.
        return ('Method not recognized', 415)
    
  


@app.route('/boats/<id>', methods=['PUT','PATCH', 'DELETE','GET'])
def boats_put_delete(id):
    # put request to change all attributes for a boat
    if request.method == 'PUT':
        content = request.get_json()
        # search for all boats to find name constraint. 403 request 
        query = client.query(kind=constants.boats)
        list_boats = query.fetch()
        for boats in list_boats:
            if boats['name'] == content['name']:
                return ("This boat already exists. Please add another one", 403)

        # check for invalid input types . 400 requests 
        if 'name' not in content.keys():
            return ('Please enter name', 400)
        if 'type' not in content.keys():
            return ('Please enter type', 400)
        if 'length' not in content.keys():
            return ('Please enter length', 400)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        client.put(boat)
        # set 303 status code. Location header is created. Code was taken from stack overflow. Citation at the beginning of code.
        return jsonify(), 303, {'Location': request.url}
    
    # patch request to change specific attributes for a boat
    elif request.method == 'PATCH':
        content = request.get_json()

        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if 'name' in content.keys():
            # search for all boats to find name constraint. 403 request 
            query = client.query(kind=constants.boats)
            list_boats = query.fetch()
            for boats in list_boats:
                if boats['name'] == content['name']:
                    return ("This boat already exists. Please add another one", 403)
                else:
                    boat['name'] = content['name']
        if 'type' in content.keys():
            boat['type'] = content['type']
        if 'length' in content.keys():
            boat['length'] = content['length']
        client.put(boat)
        boat['self'] = request.url
        return (boat, 200) # boat is returned as a JSON object. 200 request code

    
    # delete request to delete a specific boat 
    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        # confirms ID before deleting. 404 request if ID doesn't exist
        if boat is None:
            return ("This boat ID does not exist. Please try again.", 404)
        else:
            client.delete(boat_key)
            return ('Boat was deleted', 204) # Boat was successfully deleted. 204 request. 
    
    # get request to view a specific boat 
    elif request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat['id'] = id
        boat['self'] = request.url # add self URL
        if 'text/html' in request.accept_mimetypes:
            # render JSON object to text/html. Implentaton taken from stack overflow. Citation at the beginning of the code
            return render_template_string('''
            <ul>
                <li>{{ boat.id }}</li>
                <li>{{ boat.name }}</li>
                <li>{{ boat.type }}</li>
                <li>{{ boat.length }}</li>
                <li>{{ boat.self }}</li>
            </ul>
            ''', boat=boat)
        elif 'application/json' in request.accept_mimetypes:
            return (boat, 200) # boat is returned as a JSON object. 200 request code
        else:
            return ('Method not recognized', 406)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)