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

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        body = [message.to_dict() for message in Message.query.all()]
        return jsonify(body), 200
    else:
        try:
            data = request.get_json()
            message = Message(**data)
            db.session.add(message)
            db.session.commit()
            return message.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    if message := Message.query.filter(Message.id == id).first():
        if request.method == "PATCH":
            try:
                data = request.get_json()
                for attr in data:
                    setattr(message, attr, data[attr])
                db.session.add(message)
                db.session.commit()
                return message.to_dict(), 200
            except Exception as e:
                db.session.rollback()
                return {"error": str(e)}, 400
        else:
            db.session.delete(message)
            db.session.commit()
            response_body = {
                "deleted": True,
                "message": "Message was deleted."
            }
            return response_body, 200
    else:
        response_body = {
            "message": f"There is no message with id of {id} in our database."
        }
        return response_body.to_dict(), 404


if __name__ == '__main__':
    app.run(port=5555)
