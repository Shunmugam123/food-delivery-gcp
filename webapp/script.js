document.addEventListener('DOMContentLoaded', () => {
    const orderForm = document.getElementById('orderForm');
    const messageDiv = document.getElementById('message');

    orderForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        messageDiv.textContent = '';
        messageDiv.className = 'message';

        const restaurantId = document.getElementById('restaurantId').value;
        const items = document.getElementById('items').value.split(',').map(item => item.trim());
        const deliveryAddress = document.getElementById('deliveryAddress').value;

        const orderData = {
            restaurantId,
            items,
            deliveryAddress
        };

        try {
            // In a real scenario, replace this with your API Gateway endpoint
            const response = await fetch('/api/place-order', {
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
});
