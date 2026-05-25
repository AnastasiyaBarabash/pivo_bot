from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from database import (
    get_drinks, get_user_by_id, create_order,
    add_user, init_db, get_all_orders, get_drink_by_id,
    is_order_by_id, update_order_status_in_db, filter_drinks
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()
app.config['DEBUG'] = True


@app.route('/menu/', methods=['GET'])
def menu():
    drinks = get_drinks()
    return jsonify(drinks)


@app.route('/users/<int:user_id>/', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404


@app.route('/users/', methods=['POST'])
def user():
    data = request.json
    user_id = data.get('id')
    username = data.get('username')
    if not user_id or not username:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    response = add_user(user_id, username)
    return jsonify(response)


@app.route('/orders/', methods=['POST'])
def new_order():
    data = request.get_json()
    user_id = data.get("user_id")
    drink_id = data.get("drink_id")
    created_at = datetime.now()
    if not (user_id and drink_id):
        return jsonify({"error": "Missing order information"}), 400

    order_id = create_order(user_id, drink_id, created_at)
    user = get_user_by_id(user_id)
    name = user.get("username")
    alco = get_drink_by_id(drink_id)
    drink_name = alco.get("drink_name")
    created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')

    socketio.emit('new_order', {
        "id": order_id,
        "username": name,
        "drink_name": drink_name,
        "created_at": created_at_str,
        "status": "ожидает"
    })
    return jsonify({"status": "Order created", "order_id": order_id}), 201


@app.route('/orders/', methods=['GET'])
def get_orders():
    orders = get_all_orders()
    return jsonify(orders)


@app.route('/orders/<int:order_id>/', methods=['PATCH'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    order = is_order_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    updated_order = update_order_status_in_db(order_id, new_status)
    socketio.emit('order_status_updated', updated_order)
    return jsonify(updated_order)


@app.route('/filtered_cocktails/', methods=['GET'])
def get_cocktails():
    cocktails = filter_drinks(request.args.to_dict())
    return jsonify(cocktails)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=40404, debug=True)
