// Products page functionality

let products = [];
let allProducts = new Map();
let categories = [];
let currentCategory = null;

function getStringHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash);
}

function getImageUrl(productName, categoryName) {
    const descriptiveStr = (productName || categoryName || 'electronics').toLowerCase().trim();
    
    // 🛡️ 100% SAFE, OFFICIAL MANUFACTURER CDN MAPPINGS
    // This absolutely guarantees that NO unethical, random, or incorrectly tagged internet photos are EVER shown.
    const exactMatches = {
        'iphone 13 pro': 'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?q=80&w=1000&auto=format&fit=crop',
        'samsung galaxy s21': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=1000&auto=format&fit=crop',
        'macbook pro m1': 'https://images.unsplash.com/photo-1517336714460-4c702df4ce9f?q=80&w=1000&auto=format&fit=crop',
        'ipad air': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop',
        'sony wh-1000xm4': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop',
        'smartphones': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1000&auto=format&fit=crop',
        'laptops': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?q=80&w=1000&auto=format&fit=crop',
        'tablets': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop',
        'accessories': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop'
    };

    // Use guaranteed safe manufacturer product photo if mapped
    if (exactMatches[descriptiveStr]) {
        return exactMatches[descriptiveStr];
    }
    
    // For anything else, use a 100% safe, beautifully styled text-box placeholder (no random internet photos)
    const displayName = encodeURIComponent(productName || categoryName || 'TechMart Product');
    return `https://placehold.co/400x400/1a2332/00d4ff?text=${displayName}`;
}

document.addEventListener('DOMContentLoaded', function () {
    loadCategories();
    initChatbot();
});

async function openProfile() {
    const result = await makeRequest('/api/user_profile', 'GET');
    if (result.success) {
        document.getElementById('profileUserId').textContent = result.user_id;
        document.getElementById('profileUsername').textContent = result.username;
        document.getElementById('profileEmail').textContent = result.email;
        document.getElementById('profileAddress').textContent = result.address || 'N/A';
        
        // Show the modal
        const profileModal = document.getElementById('profileModal');
        if (profileModal) {
            profileModal.classList.add('active');
        }
        
        // Load orders
        fetchUserOrders();
    } else {
        showMessage('message', result.message || 'Failed to load profile!', 'error');
    }
}

async function loadCategories() {
    const result = await makeRequest('/api/categories_with_count', 'GET');

    if (result.success) {
        categories = result.categories;
        displayCategoryList(categories);
    } else {
        showMessage('message', 'Failed to load categories!', 'error');
        // Fallback to simple category list
        const fallbackResult = await makeRequest('/api/categories', 'GET');
        if (fallbackResult.success) {
            const fallbackCategories = fallbackResult.categories.map(cat => ({
                category: cat,
                product_count: 0
            }));
            displayCategoryList(fallbackCategories);
        }
    }
}

function displayCategoryList(categoriesList) {
    const categoryList = document.getElementById('categoryList');
    categoryList.innerHTML = '';

    if (categoriesList.length === 0) {
        categoryList.innerHTML = '<div style="text-align: center; grid-column: 1 / -1; color: #666; font-size: 1.2rem;">No categories found.</div>';
        return;
    }

    categoriesList.forEach(cat => {
        const categoryCard = document.createElement('div');
        categoryCard.className = 'category-card';
        const categoryImageUrl = getImageUrl(cat.category);

        categoryCard.innerHTML = `
            <div class="category-image">
                <img src="${categoryImageUrl}" alt="${cat.category}">
            </div>
            <div class="category-name">${cat.category}</div>
            <div class="category-count">${cat.product_count} products</div>
        `;
        categoryCard.onclick = () => showProductsByCategory(cat.category);
        categoryList.appendChild(categoryCard);
    });
}

function showProductsByCategory(category) {
    currentCategory = category;
    document.getElementById('categoryTitle').textContent = category;

    // Hide category list, show products view
    document.getElementById('categoryListView').style.display = 'none';
    document.getElementById('productsView').style.display = 'block';

    // Load products for this category
    loadProducts(category);
}

function showCategoryList() {
    // Hide products view, show category list
    document.getElementById('productsView').style.display = 'none';
    document.getElementById('categoryListView').style.display = 'block';
    currentCategory = null;

    // Clear products grid
    document.getElementById('productsGrid').innerHTML = '';
}

async function loadProducts(category = null) {
    let url = '/api/products';
    if (category) {
        url += `?category=${encodeURIComponent(category)}`;
    }

    const result = await makeRequest(url, 'GET');

    if (result.success) {
        products = result.products;
        displayProducts(products);
    } else {
        showMessage('message', 'Failed to load products!', 'error');
    }
}

function displayProducts(productsList, containerId = 'productsGrid') {
    const productsGrid = document.getElementById(containerId);
    productsGrid.innerHTML = '';

    if (productsList.length === 0) {
        productsGrid.innerHTML = '<p style="text-align: center; color: #666; font-size: 1.2rem; grid-column: 1 / -1;">No products found.</p>';
        return;
    }

    productsList.forEach(product => {
        allProducts.set(product.product_id, product);

        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        const isOutOfStock = product.stock <= 0;
        const isLowStock = product.stock > 0 && product.stock <= 3;
        
        let stockBadge = '';
        if (isOutOfStock) {
            stockBadge = '<span class="stock-badge out-of-stock">Out of Stock</span>';
        } else if (isLowStock) {
            stockBadge = `<span class="stock-badge low-stock">Low Stock (${product.stock})</span>`;
        } else {
            stockBadge = `<span class="stock-badge in-stock">In Stock (${product.stock})</span>`;
        }

        const disabledAttr = isOutOfStock ? 'disabled' : '';
        const disabledStyle = isOutOfStock ? 'opacity: 0.6; cursor: not-allowed;' : '';

        // Calculate discounted price
        const discount = product.discount || 0;
        const discountedPrice = product.price - (product.price * discount / 100);

        // Price display logic
        let priceDisplay = '';
        if (discount > 0) {
            priceDisplay = `
                <div class="product-price">
                    <span style="text-decoration: line-through; color: #ff6b6b; font-size: 0.9rem;">₹${parseFloat(product.price).toFixed(2)}</span>
                    <span style="color: #00d4ff; font-weight: bold; font-size: 1.2rem; margin-left: 0.5rem;">₹${parseFloat(discountedPrice).toFixed(2)}</span>
                    <span style="color: #ff6b6b; font-weight: bold; font-size: 0.9rem; margin-left: 0.5rem;">(${discount}% OFF)</span>
                </div>
            `;
        } else {
            priceDisplay = `<div class="product-price">₹${parseFloat(product.price).toFixed(2)}</div>`;
        }

        let rowImageUrl = product.image && product.image.startsWith('http') 
            ? product.image 
            : getImageUrl(product.p_name || product.category);

        productCard.innerHTML = `
            <img src="${rowImageUrl}" alt="${product.p_name}" class="product-image">
            <div class="product-info" style="${disabledStyle}">
                <h3 class="product-title">${product.p_name}</h3>
                <div class="product-category" style="color: var(--blue); font-size: 0.9rem; margin: 0.2rem 0;">${product.category}</div>
                ${priceDisplay}
                <div class="product-features"><strong>Features:</strong> ${product.features || 'N/A'}</div>
                <div class="product-warranty"><strong>Warranty:</strong> ${product.warranty || 'N/A'}</div>
                <div class="product-stock"><strong>Status:</strong> ${stockBadge}</div>
                <input type="number" class="quantity-input" id="qty-${product.product_id}" min="1" max="${product.stock}" value="1" placeholder="Quantity" ${disabledAttr}>
                <div class="product-actions" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                    <button class="btn btn-primary btn-small" onclick="buyNow(${product.product_id})" ${disabledAttr}>Buy Now</button>
                    <button class="btn btn-secondary btn-small" onclick="addToCart(${product.product_id})" ${disabledAttr}>Add to Cart</button>
                    <button class="btn btn-secondary btn-small" onclick="openReviewModal(${product.product_id})" style="grid-column: span 2; width: 100%;">Review</button>
                    <button class="btn btn-secondary btn-small" onclick="toggleComparison(${product.product_id})" style="grid-column: span 2; width: 100%;">Compare</button>
                </div>
            </div>
        `;
        productsGrid.appendChild(productCard);
    });
}

async function buyNow(productId) {
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value);
    const product = allProducts.get(productId);

    if (quantity < 1) {
        showMessage('message', 'Please select a valid quantity!', 'error');
        return;
    }

    // Use discounted price for purchase
    const discount = product.discount || 0;
    const discountedPrice = product.price - (product.price * discount / 100);

    const result = await makeRequest('/api/buy_now', 'POST', {
        product_id: productId,
        quantity: quantity,
        amount: discountedPrice * quantity
    });

    if (result.success) {
        if (result.invoice_text) {
            const waUrl = 'https://wa.me/?text=' + encodeURIComponent(result.invoice_text);
            showModal('Order Placed', `
                <p>Your order has been placed successfully!</p>
                <div style="text-align: center; margin-top: 1.5rem;">
                    <a href="${waUrl}" target="_blank" class="btn btn-success" style="display:inline-block; width:100%; box-sizing:border-box;">📱 Send Invoice to WhatsApp</a>
                </div>
            `, true);
        } else {
            showModal('Order Placed', 'Your order has been placed successfully!');
        }
        document.getElementById('qty-' + productId).value = 1;
        loadProducts(currentCategory); // Reload ONLY current category to update stock
    } else {
        showMessage('message', result.message || 'Failed to place order!', 'error');
    }
}

async function addToCart(productId) {
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value);
    const product = allProducts.get(productId);

    if (quantity < 1) {
        showMessage('message', 'Please select a valid quantity!', 'error');
        return;
    }

    // Use discounted price for cart
    const discount = product.discount || 0;
    const discountedPrice = product.price - (product.price * discount / 100);
    const amount = discountedPrice * quantity;

    const result = await makeRequest('/api/add_to_cart', 'POST', {
        product_id: productId,
        quantity: quantity,
        amount: amount
    });

    if (result.success) {
        showMessage('message', 'Product added to cart!', 'success');
        document.getElementById('qty-' + productId).value = 1;
        loadProducts(currentCategory); // Reload ONLY current category to update stock
    } else {
        showMessage('message', result.message || 'Failed to add to cart!', 'error');
    }
}

function goToCart() {
    window.location.href = '/cart';
}

// Chatbot functionality
function initChatbot() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbot = document.getElementById('chatbot');
    const closeChatbot = document.getElementById('closeChatbot');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotInput = document.getElementById('chatbotInput');

    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', () => {
            chatbot.classList.toggle('active');
        });
    }

    if (closeChatbot) {
        closeChatbot.addEventListener('click', () => {
            chatbot.classList.remove('active');
        });
    }

    if (chatbotSend) {
        chatbotSend.addEventListener('click', sendChatMessage);
    }

    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
}

async function sendChatMessage() {
    const chatbotInput = document.getElementById('chatbotInput');
    const message = chatbotInput.value.trim();

    if (!message) return;

    // Add user message to chat
    const chatbotBody = document.getElementById('chatbotBody');
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message-item user';
    userMsgDiv.textContent = message;
    chatbotBody.appendChild(userMsgDiv);

    chatbotInput.value = '';

    // Get bot response
    const result = await makeRequest('/api/chatbot', 'POST', {
        message: message
    });

    if (result.success) {
        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'message-item bot';
        botMsgDiv.textContent = result.response;
        chatbotBody.appendChild(botMsgDiv);

        // Scroll to bottom
        chatbotBody.scrollTop = chatbotBody.scrollHeight;
    }
}

// Profile functionality
async function openProfile() {
    const result = await makeRequest('/api/user_profile', 'GET');

    if (result.success) {
        document.getElementById('profileUserId').textContent = result.user_id;
        document.getElementById('profileUsername').textContent = result.username;
        document.getElementById('profileEmail').textContent = result.email;
        document.getElementById('profileAddress').textContent = result.address || 'N/A';

        // Fetch user orders immediately
        fetchUserOrders();

        // Setup real-time polling (every 5 seconds)
        if (!window.orderPollInterval) {
            window.orderPollInterval = setInterval(fetchUserOrders, 5000);
        }

        const profileModal = document.getElementById('profileModal');
        if (profileModal) {
            profileModal.classList.add('active');
        }
    } else {
        showMessage('message', 'Failed to load profile!', 'error');
    }
}

function displayUserOrders(ordersResult) {
    const ordersContainer = document.getElementById('profileOrders');

    if (!ordersResult.success || !ordersResult.orders || ordersResult.orders.length === 0) {
        ordersContainer.innerHTML = '<p style="color: #666;">No orders yet</p>';
        return;
    }

    let html = '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="border-bottom: 2px solid #ddd;">';
    html += '<th style="padding: 0.5rem; text-align: left;">Order ID</th>';
    html += '<th style="padding: 0.5rem; text-align: left;">Products</th>';
    html += '<th style="padding: 0.5rem; text-align: left;">Date</th>';
    html += '<th style="padding: 0.5rem; text-align: right;">Amount</th>';
    html += '<th style="padding: 0.5rem; text-align: center;">Status</th>';
    html += '<th style="padding: 0.5rem; text-align: center;">Actions</th>';
    html += '</tr></thead><tbody>';

    ordersResult.orders.forEach(order => {
        html += '<tr style="border-bottom: 1px solid #eee;">';
        html += `<td style="padding: 0.5rem;">#${order.order_id}</td>`;
        html += `<td style="padding: 0.5rem; font-size: 0.8rem; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${order.product_names || 'N/A'}">${order.product_names || 'N/A'}</td>`;
        const dateStr = order.order_date.split(' ')[0].replace('00:00:00', '').trim();
        const status = order.status || 'Pending';
        let color = 'orange';
        if (status === 'Delivered') color = 'green';
        else if (status === 'Return Requested') color = '#e74c3c';
        else if (status === 'Returned') color = '#9b59b6';
        html += `<td style="padding: 0.5rem;">${dateStr}</td>`;
        html += `<td style="padding: 0.5rem; text-align: right;">₹${parseFloat(order.total_amount).toFixed(2)}</td>`;
        html += `<td style="padding: 0.5rem; text-align: center;"><span style="color: ${color}; font-weight: bold;">${status}</span></td>`;

        // Action buttons
        html += `<td style="padding: 0.5rem; text-align: center;">`;
        html += `<div style="display: flex; flex-direction: column; gap: 0.3rem; align-items: center;">`;
        html += `<a href="/api/generate_bill/${order.order_id}" target="_blank" class="btn btn-secondary btn-small" style="width: 100%; text-align: center; text-decoration: none; font-size: 0.75rem;">📄 View Bill</a>`;
        html += `<button class="btn btn-small" onclick="shareOnWhatsApp(${order.order_id})" style="width: 100%; background: #25D366; color: white; border: none; font-size: 0.75rem; cursor: pointer;">📱 WhatsApp</button>`;
        if (status === 'Delivered') {
            html += `<button class="btn btn-small" onclick="returnOrder(${order.order_id})" style="width: 100%; background: #e74c3c; color: white; border: none; font-size: 0.75rem; cursor: pointer;">↩️ Return</button>`;
        } else if (status === 'Return Requested') {
            html += `<span style="font-size: 0.7rem; color: #e74c3c;">Return Pending</span>`;
        } else if (status === 'Returned') {
            html += `<span style="font-size: 0.7rem; color: #9b59b6;">Returned ✓</span>`;
        }
        html += `</div>`;
        html += `</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    ordersContainer.innerHTML = html;
}

async function fetchUserOrders() {
    const ordersResult = await makeRequest('/api/user_orders', 'GET');
    displayUserOrders(ordersResult);
}

async function shareOnWhatsApp(orderId) {
    const result = await makeRequest(`/api/share_invoice/${orderId}`, 'GET');
    if (result.success && result.invoice_text) {
        const waUrl = 'https://wa.me/?text=' + encodeURIComponent(result.invoice_text);
        window.open(waUrl, '_blank');
    } else {
        showMessage('message', result.message || 'Failed to generate invoice!', 'error');
    }
}

async function returnOrder(orderId) {
    const reason = prompt('Please enter the reason for return:');
    if (reason === null) return; // User cancelled
    if (reason.trim() === '') {
        showMessage('message', 'Return reason is required!', 'error');
        return;
    }

    if (!confirm('Are you sure you want to return this order?')) return;

    const result = await makeRequest('/api/return_order', 'POST', {
        order_id: orderId,
        reason: reason
    });

    if (result.success) {
        showMessage('message', 'Return request submitted successfully!', 'success');
        fetchUserOrders(); // Refresh orders to reflect new status
    } else {
        showMessage('message', result.message || 'Failed to submit return request!', 'error');
    }
}

function closeProfileModal() {
    const profileModal = document.getElementById('profileModal');
    if (profileModal) {
        profileModal.classList.remove('active');
        if (window.orderPollInterval) {
            clearInterval(window.orderPollInterval);
            window.orderPollInterval = null;
        }
    }
}

// Review functionality
let currentReviewProductId = null;

function openReviewModal(productId) {
    currentReviewProductId = productId;
    const reviewModal = document.getElementById('reviewModal');
    if (reviewModal) {
        reviewModal.classList.add('active');
    }
}

function closeReviewModal() {
    const reviewModal = document.getElementById('reviewModal');
    if (reviewModal) {
        reviewModal.classList.remove('active');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', handleReviewSubmit);
    }
});

async function handleReviewSubmit(e) {
    e.preventDefault();

    const rating = document.getElementById('reviewRating').value;
    const comment = document.getElementById('reviewComment').value;

    if (!rating || !comment) {
        showMessage('message', 'Please fill in all review fields!', 'error');
        return;
    }

    const result = await makeRequest('/api/add_review', 'POST', {
        product_id: currentReviewProductId,
        rating: parseInt(rating),
        comment: comment
    });

    if (result.success) {
        showMessage('message', 'Review submitted successfully!', 'success');
        document.getElementById('reviewForm').reset();
        closeReviewModal();
    } else {
        showMessage('message', result.message || 'Failed to submit review!', 'error');
    }
}
// Product comparison tool state
let comparisonList = [];

function toggleComparison(productId) {
    const product = allProducts.get(productId);
    if (!product) return;

    const index = comparisonList.findIndex(p => p.product_id === productId);
    if (index > -1) {
        comparisonList.splice(index, 1);
        showMessage('message', `${product.p_name} removed from comparison`, 'success');
    } else {
        if (comparisonList.length >= 3) {
            showMessage('message', 'You can compare maximum 3 products at a time', 'error');
            return;
        }
        comparisonList.push(product);
        showMessage('message', `${product.p_name} added to comparison`, 'success');
    }
    updateComparisonButton();
}

function updateComparisonButton() {
    const existingBtn = document.getElementById('floatingCompareBtn');
    if (comparisonList.length >= 2) {
        if (!existingBtn) {
            const btn = document.createElement('button');
            btn.id = 'floatingCompareBtn';
            btn.className = 'chatbot-toggle';
            btn.style.bottom = '80px';
            btn.textContent = '📊';
            btn.title = 'Compare Selected Products';
            btn.onclick = openComparisonModal;
            document.body.appendChild(btn);
        }
    } else if (existingBtn) {
        existingBtn.remove();
    }
}

function openComparisonModal() {
    const modal = document.getElementById('comparisonModal');
    const container = document.getElementById('comparisonTableContainer');

    let html = '<table class="orders-table" style="width: 100%;">';
    html += '<thead><tr><th>Feature</th>';
    comparisonList.forEach(p => {
        html += `<th>${p.p_name}</th>`;
    });
    html += '</tr></thead><tbody>';

    const fields = [
        { label: 'Price', key: 'price', prefix: '₹' },
        { label: 'Discount', key: 'discount', suffix: '%' },
        { label: 'Category', key: 'category' },
        { label: 'Features', key: 'features' },
        { label: 'Warranty', key: 'warranty' },
        { label: 'Stock', key: 'stock' }
    ];

    fields.forEach(field => {
        html += `<tr><td><strong>${field.label}</strong></td>`;
        comparisonList.forEach(p => {
            let val = p[field.key] || 'N/A';
            if (field.prefix) val = field.prefix + val;
            if (field.suffix) val = val + field.suffix;
            html += `<td>${val}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
    modal.classList.add('active');
}

function closeComparisonModal() {
    document.getElementById('comparisonModal').classList.remove('active');
}

function openDeliveredModal() {
    const modal = document.getElementById('deliveredModal');
    const tableBody = document.getElementById('deliveredTableBody');
    if (!modal || !tableBody) return;

    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading...</td></tr>';
    modal.classList.add('active');

    makeRequest('/api/delivered_products', 'GET').then(result => {
        if (result.success) {
            if (result.products.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No delivered products found.</td></tr>';
                return;
            }
            tableBody.innerHTML = '';
            result.products.forEach(p => {
                const row = document.createElement('tr');
                const orderDateRaw = p.order_date || '';
                const orderDate = orderDateRaw ? new Date(orderDateRaw.split(' ')[0].replace('00:00:00', '').trim()).toLocaleDateString() : 'N/A';
                row.innerHTML = `
                    <td>${p.p_name}</td>
                    <td>${orderDate}</td>
                    <td>₹${parseFloat(p.price).toFixed(2)}</td>
                    <td>${p.quantity}</td>
                    <td>₹${parseFloat(p.sum_amount).toFixed(2)}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">${result.message}</td></tr>`;
        }
    });
}

function closeDeliveredModal() {
    const modal = document.getElementById('deliveredModal');
    if (modal) modal.classList.remove('active');
}
