from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import desc, asc

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET','POST'])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by(asc(Message.created_at)).all()

        if not messages:
            return {'Error': 'There are no messages in the database.'}, 404

        message_dicts = [m.to_dict() for m in messages]
        return make_response(jsonify(message_dicts), 200)
    
    elif request.method == "POST":
        new_message = Message()
        try:
            for key in request.get_json():
                setattr(new_message, key, request.get_json()[key])
            db.session.add(new_message)
            db.session.commit()
            return make_response(jsonify(new_message.to_dict()), 201)
        except Exception as e:
            return {'Error': f'Error {e} has occured.'}

@app.route('/messages/<int:id>', methods=["GET", "PATCH", "DELETE"])
def messages_by_id(id: int):
    if request.method == "GET":
        message = db.session.get(Message, id)

        if not message:
            return {'Error': f'Message with id {id} does not currently exist.'}, 404

        return make_response(jsonify(message.to_dict()), 200)
    elif request.method == "PATCH":
        message = Message.query.get(id)

        if not message:
            return {'Error': f'Message with id {id} does not exist.'}, 404

        for key in request.get_json():
            setattr(message, key, request.get_json()[key])
        
        db.session.add(message)
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == "DELETE":
        message = db.session.get(Message, id)

        if not message:
            return {'Error': f'Message with id {id} does not exist.'}, 404

        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({}), 204)


if __name__ == '__main__':
    app.run(port=5555)
