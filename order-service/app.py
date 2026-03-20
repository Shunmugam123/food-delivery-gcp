from flask import Flask, request, jsonify
import os
import uuid
from google.cloud import pubsub_v1
import json

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def health_check():
    return "Order Service is running!"

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used when deploying to Cloud Run.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
