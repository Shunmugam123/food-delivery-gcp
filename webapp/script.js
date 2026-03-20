document.addEventListener('DOMContentLoaded', () => {
    const orderForm = document.getElementById('orderForm');
    const messageDiv = document.getElementById('message');

    // New UI elements for order status
    const orderStatusSection = document.getElementById('orderStatusSection');
    const orderIdDisplay = document.getElementById('orderIdDisplay');
    const orderStatusDisplay = document.getElementById('orderStatusDisplay');
    const waitingTimeDisplay = document.getElementById('waitingTimeDisplay');
    const updateStatusBtn = document.getElementById('updateStatusBtn');
    const newStatusSelect = document.getElementById('newStatusSelect');

    let currentOrderId = null;
    let pollingInterval = null;

    const stopPolling = () => {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    };

    const startPolling = (orderId) => {
        stopPolling(); // Stop any existing polling
        currentOrderId = orderId;
        orderStatusSection.style.display = 'block'; // Show the order status section

        const fetchOrderStatus = async () => {
            try {
                const response = await fetch(`/orders/${currentOrderId}`);
                if (response.ok) {
                    const order = await response.json();
                    orderIdDisplay.textContent = order.orderId;
                    orderStatusDisplay.textContent = order.status;
                    waitingTimeDisplay.textContent = order.estimatedWaitingTime;

                    if (order.status === 'DELIVERED') {
                        stopPolling();
                        messageDiv.textContent = 'Order has been delivered!';
                        messageDiv.classList.add('success');
                        updateStatusBtn.style.display = 'none'; // Hide update button after delivery
                        newStatusSelect.style.display = 'none'; // Hide status select after delivery
                    }
                } else {
                    const errorData = await response.json();
                    messageDiv.textContent = `Error fetching order status: ${errorData.message || response.statusText}`;
                    messageDiv.classList.add('error');
                    stopPolling(); // Stop polling on error
                }
            } catch (error) {
                messageDiv.textContent = `Network error during polling: ${error.message}`;
                messageDiv.classList.add('error');
                stopPolling(); // Stop polling on network error
            }
        };

        pollingInterval = setInterval(fetchOrderStatus, 2000); // Poll every 2 seconds
        fetchOrderStatus(); // Fetch immediately on start
    };

    orderForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        messageDiv.textContent = '';
        messageDiv.className = 'message';
        orderStatusSection.style.display = 'none'; // Hide status section initially

        const restaurantId = document.getElementById('restaurantId').value;
        const items = document.getElementById('items').value.split(',').map(item => item.trim());
        const deliveryAddress = document.getElementById('deliveryAddress').value;

        const orderData = {
            restaurantId,
            items,
            deliveryAddress
        };

        try {
            const response = await fetch('/place-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData),
            });

            if (response.ok) {
                const result = await response.json();
                messageDiv.textContent = `Order placed successfully! Order ID: ${result.orderId}`;
                messageDiv.classList.add('success');
                orderForm.reset();

                // Start polling for the new order's status
                startPolling(result.orderId);
                
                // Show manual update controls
                updateStatusBtn.style.display = 'inline-block';
                newStatusSelect.style.display = 'inline-block';

            } else {
                const errorData = await response.json();
                messageDiv.textContent = `Error placing order: ${errorData.message || response.statusText}`;
                messageDiv.classList.add('error');
            }
        } catch (error) {
            messageDiv.textContent = `Network error: ${error.message}`;
            messageDiv.classList.add('error');
        }
    });

    // Event listener for manual status update button
    updateStatusBtn.addEventListener('click', async () => {
        if (!currentOrderId) {
            messageDiv.textContent = 'No order to update.';
            messageDiv.classList.add('error');
            return;
        }

        const newStatus = newStatusSelect.value;
        try {
            const response = await fetch(`/orders/${currentOrderId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus }),
            });

            if (response.ok) {
                const result = await response.json();
                messageDiv.textContent = `Order ${currentOrderId} status updated to ${newStatus}!`;
                messageDiv.classList.add('success');
                // Immediately refetch status to reflect change
                startPolling(currentOrderId); 
            } else {
                const errorData = await response.json();
                messageDiv.textContent = `Error updating status: ${errorData.message || response.statusText}`;
                messageDiv.classList.add('error');
            }
        } catch (error) {
            messageDiv.textContent = `Network error updating status: ${error.message}`;
            messageDiv.classList.add('error');
        }
    });
});