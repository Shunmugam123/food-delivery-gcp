# Figgy Delivery GCP

This repository contains the implementation of a food delivery application designed to run on Google Cloud Platform (GCP).

## Architecture Overview

The system leverages several GCP services to provide a scalable and robust solution:

- **User Service (Cloud Run):** Handles user-related operations, including user registration, login, and profile management.
- **API Gateway:** Acts as the entry point for all external requests, routing them to the appropriate backend services.
- **Order Service (Cloud Run):** Manages order creation and status checks.
- **Order Processing (Pub/Sub):** An event-driven mechanism where new order events are published to Pub/Sub.
- **Restaurant Service (Cloud Function):** Subscribes to order events from Pub/Sub to accept or reject orders.
- **Delivery Service (Cloud Function + Cloud Tasks):** Assigns delivery agents and updates order statuses after a delay, utilizing Cloud Tasks for delayed operations.
- **Database (Firestore):** A NoSQL document database used to store application data, including `users`, `orders`, and `restaurants` collections.
- **Delivery Simulation (Cloud Tasks):** Used for simulating delivery processes and managing timed events.

## Workflow

1. **Place Order:** User interacts with the API Gateway, which routes the request to the Order Service (Cloud Run).
2. **Order Created Event:** Upon successful order creation, an event is published to Pub/Sub.
3. **Restaurant Action:** The Restaurant Service (Cloud Function) consumes the Pub/Sub event, processes the order, and decides to accept or reject it.
4. **Delivery Assignment:** The Delivery Service (Cloud Function) is triggered to assign a delivery agent, potentially using Cloud Tasks for delayed status updates.
5. **Status Updates:** Order status updates are managed and stored in Firestore.