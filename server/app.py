from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return "Index for messages API"

@app.route('/messages', methods = ["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by(Message.created_at).all()

        messages_list =[message.to_dict() for message in messages]

        response = make_response(jsonify(messages_list), 200)

        response.headers["Content-Type"] ="application/json"

        return response
    
    elif request.method == "POST":
        data = request.get_json()
        body = data.get("body")
        username = data.get("username")

        if not body or not username:
            return make_response(jsonify({"error": "Both body and username should be provided"}))

        new_message =Message(body = body, username = username)
        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()
        

        response = make_response(jsonify(message_dict), 201)

        response.headers["Content-Type"] ="application/json"
        
        return response




@app.route('/messages/<int:id>', methods = ["GET", "PATCH", "DELETE"])
def message_by_id(id):

    message = Message.query.filter_by(id=id).first()

    if not message:

        return make_response(jsonify({"error": "Message not found."}), 404)

    if request.method == "GET":
       message_dict = message.to_dict()

       response = make_response(jsonify(message_dict), 200)

       response.headers["Content-Type"] = "application/json"

       return response
    
    elif request.method == "PATCH":

        data = request.get_json()
        new_body = data.get("body")

        if not new_body:
            return make_response(jsonify(
                {"error":"The 'body' parameter is required to change for updating the message"}),
                404)
        message.body = new_body
        db.session.commit()

        updated_message_dict =message.to_dict()

        response = make_response(jsonify(updated_message_dict), 200)

        response.headers["Content-Type"] = "application/json"

        return response
    
    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()

        response = make_response(jsonify({"message": "Message successfully deleted"}), 200)


        return response


if __name__ == '__main__':
    app.run(port=5555)
