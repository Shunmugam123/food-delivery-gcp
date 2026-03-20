from flask import Flask, request, jsonify
import os
import uuid
from google.cloud import pubsub_v1
import json
from datetime import datetime # Import datetime

app = Flask(__name__)

# In-memory storage for orders {order_id: order_details}
orders = {}

# Placeholder for Pub/Sub publisher client
# In a real application, this would be initialized correctly with credentials
# and project ID.
publisher = None
if os.getenv("GAE_ENV", "").startswith("standard") or os.getenv("K_SERVICE"):
    # Running on Google Cloud (App Engine or Cloud Run)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    topic_name = "order-processing-topic" # This topic needs to be created in GCP
    if project_id:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
    else:
        print("GOOGLE_CLOUD_PROJECT environment variable not set. Pub/Sub will not be available.")
else:
    # Running locally or in a development environment
    print("Running locally. Pub/Sub client not initialized. Orders will not be published to Pub/Sub.")
    # For local development, you might use a mock or skip Pub/Sub publishing

@app.route('/place-order', methods=['POST'])
def place_order():
    """
    Handles requests to place a new order.
    Expects JSON input with restaurantId, items, and deliveryAddress.
    """
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json()
    restaurant_id = data.get('restaurantId')
    items = data.get('items')
    delivery_address = data.get('deliveryAddress')

    if not all([restaurant_id, items, delivery_address]):
        return jsonify({"message": "Missing required order information"}), 400

    order_id = str(uuid.uuid4())
    current_time = datetime.now()

    # Store order in in-memory dictionary
    orders[order_id] = {
        "orderId": order_id,
        "restaurantId": restaurant_id,
        "items": items,
        "deliveryAddress": delivery_address,
        "status": "ORDER_PLACED",
        "timestamp": current_time.isoformat(), # Store creation time
        "estimatedWaitingTime": 30 # Initial estimate in minutes
    }
    print(f"Received order for Restaurant ID: {restaurant_id}, Order ID: {order_id}")

    # Simulate publishing to Pub/Sub
    if publisher:
        try:
            message_data = {
                "orderId": order_id,
                "restaurantId": restaurant_id,
                "items": items,
                "deliveryAddress": delivery_address,
                "status": "ORDER_PLACED"
            }
            future = publisher.publish(topic_path, json.dumps(message_data).encode("utf-8"))
            print(f"Message published to Pub/Sub with ID: {future.result()}")
        except Exception as e:
            print(f"Error publishing to Pub/Sub: {e}")
            # Even if Pub/Sub fails, we still consider the order "placed" for this simple demo
            # In a real system, you'd handle this more robustly (e.g., retry, dead-letter queue)

    return jsonify({"message": "Order placed successfully", "orderId": order_id}), 200

@app.route('/orders/<order_id>', methods=['GET'])
def get_order_status(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # Calculate remaining waiting time
    # For demonstration, let's assume it reduces by 1 minute for every 10 seconds passed
    order_timestamp = datetime.fromisoformat(order["timestamp"])
    time_elapsed = (datetime.now() - order_timestamp).total_seconds()
    minutes_elapsed = int(time_elapsed / 10) # 1 minute reduction for every 10 seconds for demo

    remaining_time = max(0, order["estimatedWaitingTime"] - minutes_elapsed)
    
    # Return a copy to avoid modifying the stored order directly in this endpoint
    current_order_status = order.copy()
    current_order_status["estimatedWaitingTime"] = remaining_time
    
    return jsonify(current_order_status), 200

@app.route('/', methods=['GET'])
def health_check():
    return "Order Service is running!"

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used when deploying to Cloud Run.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
