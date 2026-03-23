// Cart page functionality

document.addEventListener('DOMContentLoaded', function () {
    loadCart();
});

async function loadCart() {
    const result = await makeRequest('/api/get_cart', 'GET');

    if (result.success) {
        displayCart(result.cart);
    } else {
        showMessage('message', result.message || 'Failed to load cart!', 'error');
    }
}

function displayCart(cartItems) {
    const cartContainer = document.getElementById('cartItems');
    const cartTotalDiv = document.getElementById('cartTotal');

    cartContainer.innerHTML = '';

    if (cartItems.length === 0) {
        cartContainer.innerHTML = '<p>Your cart is empty</p>';
        cartTotalDiv.style.display = 'none';
        return;
    }

    let total = 0;

    cartItems.forEach(item => {
        total += parseFloat(item.amount);

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';

        // Calculate discounted price for display
        const discount = item.discount || 0;
        const discountedPrice = item.discounted_price || (item.price - (item.price * discount / 100));

        cartItem.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.p_name}</div>
                <div>Quantity: <strong>${item.quantity}</strong></div>
                <div class="cart-item-price">
                    ${discount > 0 ?
                `<span style="text-decoration: line-through; color: #ff6b6b;">₹${parseFloat(item.price).toFixed(2)}</span>
                         <span style="color: #00d4ff; margin-left: 0.5rem;">₹${parseFloat(discountedPrice).toFixed(2)} each</span>
                         <span style="color: #ff6b6b; font-size: 0.9rem; margin-left: 0.5rem;">(${discount}% OFF)</span>` :
                `₹${parseFloat(item.price).toFixed(2)} each`}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; font-weight: bold; color: var(--dark-green); margin-bottom: 0.5rem;">
                    ₹${parseFloat(item.amount).toFixed(2)}
                </div>
                <button class="btn btn-secondary btn-small" onclick="removeFromCart(${item.product_id})">Remove</button>
            </div>
        `;
        cartContainer.appendChild(cartItem);
    });

    cartTotalDiv.innerHTML = `
        <div>Total Amount:</div>
        <div>₹${total.toFixed(2)}</div>
    `;
    cartTotalDiv.style.display = 'flex';

    // Add checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.onclick = checkout;
    }
}

async function removeFromCart(productId) {
    const result = await makeRequest('/api/remove_from_cart', 'POST', {
        product_id: productId
    });

    if (result.success) {
        showMessage('message', 'Product removed from cart!', 'success');
        loadCart();
    } else {
        showMessage('message', result.message || 'Failed to remove product!', 'error');
    }
}

async function checkout() {
    const result = await makeRequest('/api/checkout', 'POST');

    if (result.success) {
        if (result.invoice_text) {
            const waUrl = 'https://wa.me/?text=' + encodeURIComponent(result.invoice_text);
            showModal('Order Placed', `
                <p>Your order has been placed successfully! Order ID: ${result.order_id}</p>
                <div style="text-align: center; margin-top: 1.5rem;">
                    <a href="${waUrl}" target="_blank" class="btn btn-success" style="display:inline-block; width:100%; box-sizing:border-box;">📱 Send Invoice to WhatsApp</a>
                </div>
            `, true);
        } else {
            showModal('Order Placed', `Your order has been placed successfully! Order ID: ${result.order_id}`);
        }
        setTimeout(() => {
            loadCart();
        }, 2000);
    } else {
        showMessage('message', result.message || 'Checkout failed!', 'error');
    }
}
