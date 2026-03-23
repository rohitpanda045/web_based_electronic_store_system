// Admin page functionality
let currentSection = 'analyticsSection';

function getImageUrl(image) {
    if (!image) return '/static/images/default_category.jpg';
    if (image.startsWith('http://') || image.startsWith('https://')) {
        return image;
    }
    return `/static/images/${image}`;
}

document.addEventListener('DOMContentLoaded', function () {
    // Section management
    window.showSection = function (sectionId) {
        document.querySelectorAll('.admin-section').forEach(section => {
            section.style.display = 'none';
        });
        document.getElementById(sectionId).style.display = 'block';

        if (sectionId === 'analyticsSection') loadAnalytics();
        if (sectionId === 'categoriesSection') loadCategories();
        if (sectionId === 'productsSection') loadProducts();
        if (sectionId === 'ordersSection') loadOrders();
        if (sectionId === 'deliveredSection') loadDeliveredProducts();
        if (sectionId === 'usersSection') loadUsers();
    };

    const addProductForm = document.getElementById('addProductForm');
    if (addProductForm) {
        addProductForm.addEventListener('submit', handleAddProduct);
    }
    const editProductForm = document.getElementById('editProductForm');
    if (editProductForm) {
        editProductForm.addEventListener('submit', handleEditProduct);
    }
    const addCategoryForm = document.getElementById('addCategoryForm');
    if (addCategoryForm) {
        addCategoryForm.addEventListener('submit', handleAddCategory);
    }
    const editCategoryImageForm = document.getElementById('editCategoryImageForm');
    if (editCategoryImageForm) {
        editCategoryImageForm.addEventListener('submit', handleEditCategoryImage);
    }

    // Initial load
    showSection('analyticsSection');
});

async function loadAnalytics() {
    const result = await makeRequest('/api/admin/analytics', 'GET');
    if (result.success) {
        document.getElementById('totalSales').textContent = `₹${parseFloat(result.total_sales).toFixed(2)}`;
        document.getElementById('totalOrdersCount').textContent = result.total_orders;
        document.getElementById('totalUsersCount').textContent = result.total_users;
    }
}

async function handleAddProduct(e) {
    e.preventDefault();

    const product = {
        p_name: document.getElementById('productName').value,
        price: parseFloat(document.getElementById('price').value),
        discount: parseFloat(document.getElementById('discount').value) || 0,
        stock: parseInt(document.getElementById('stock').value),
        image: document.getElementById('image').value,
        features: document.getElementById('features').value,
        warranty: document.getElementById('warranty').value,
        category: document.getElementById('category').value
    };

    const result = await makeRequest('/api/add_product', 'POST', product);

    if (result.success) {
        showMessage('message', 'Product added successfully!', 'success');
        document.getElementById('addProductForm').reset();
        closeAddProductModal(); // Explicitly close modal
        loadProducts(); // Refresh to show updated list
        // Reset category dropdown
        loadCategoryDropdown();
    } else {
        showMessage('message', result.message || 'Failed to add product!', 'error');
    }
}

async function loadOrders() {
    const result = await makeRequest('/api/get_all_orders', 'GET');

    if (result.success) {
        displayOrders(result.orders);
    } else {
        showMessage('message', result.message || 'Failed to load orders!', 'error');
    }
}

function displayOrders(orders) {
    const ordersTableBody = document.getElementById('ordersTableBody');
    ordersTableBody.innerHTML = '';

    if (orders.length === 0) {
        ordersTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No orders found</td></tr>';
        return;
    }

    orders.forEach(order => {
        const row = document.createElement('tr');
        const status = order.status || 'Pending';
        const statuses = ['Pending', 'Shipped', 'On the way', 'Out for delivery', 'Delivered', 'Return Requested', 'Returned'];

        let statusDropdown = `<select onchange="updateOrderStatus(${order.order_id}, this.value)" style="padding: 0.5rem; border-radius: 4px; background: var(--bg-dark); color: var(--text-dark); border: 1px solid #2a3f5f; cursor: pointer; min-width: 150px;">`;
        statuses.forEach(s => {
            statusDropdown += `<option value="${s}" ${s === status ? 'selected' : ''}>${s}</option>`;
        });
        statusDropdown += `</select>`;

        row.innerHTML = `
            <td>${order.order_id}</td>
            <td>${order.username}</td>
            <td>${order.product_names || '<span style="color: #888; font-style: italic;">[Product Deleted]</span>'}</td>
            <td>${order.order_date}</td>
            <td>₹${parseFloat(order.total_amount).toFixed(2)}</td>
            <td>${statusDropdown}</td>
            <td style="display: flex; flex-direction: column; gap: 0.5rem; width: 100%;">
                <button class="btn btn-secondary btn-action" onclick="viewOrderDetails(${order.order_id})" style="width: 100%;">Details</button>
                <a href="/api/generate_bill/${order.order_id}" target="_blank" class="btn btn-secondary btn-action" style="width: 100%; text-align: center; text-decoration: none;">View Bill</a>
            </td>
        `;
        ordersTableBody.appendChild(row);
    });
}

async function viewOrderDetails(orderId) {
    const result = await makeRequest(`/api/get_order_details/${orderId}`, 'GET');

    if (result.success) {
        let details = 'Order Items:\n';
        result.items.forEach(item => {
            details += `\n${item.p_name} - Qty: ${item.quantity} - ₹${parseFloat(item.sum_amount).toFixed(2)}`;
        });

        if (result.return_reason) {
            details += `\n\n---------------------------\n📝 Return Reason: ${result.return_reason}`;
        }

        showModal('Order Details', details.replace(/\n/g, '\n'));
    } else {
        showMessage('message', result.message || 'Failed to load order details!', 'error');
    }
}

// Update order status
async function updateOrderStatus(orderId, status) {
    const result = await makeRequest('/api/update_order_status', 'POST', {
        order_id: orderId,
        status: status
    });

    if (result.success) {
        showMessage('message', `Order status updated to ${status}!`, 'success');
        if (status === 'Delivered') {
            loadDeliveredProducts();
        }
    } else {
        showMessage('message', result.message || 'Failed to update order status!', 'error');
        loadOrders();
    }
}

async function loadDeliveredProducts() {
    const result = await makeRequest('/api/admin/delivered_products', 'GET');
    if (result.success) {
        displayDeliveredProducts(result.products);
    } else {
        showMessage('message', result.message || 'Failed to load delivered products!', 'error');
    }
}

function displayDeliveredProducts(products) {
    const tbody = document.getElementById('deliveredTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No delivered products found</td></tr>';
        return;
    }

    products.forEach(product => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${product.order_id}</td>
            <td>${product.username}</td>
            <td>${product.p_name}</td>
            <td>${product.quantity}</td>
            <td>₹${parseFloat(product.sum_amount).toFixed(2)}</td>
            <td>${product.order_date}</td>
        `;
        tbody.appendChild(row);
    });
}

// Edit product functions
function openEditProductModal(productId, product) {
    document.getElementById('editProductId').value = productId;
    document.getElementById('editProductName').value = product.p_name;
    document.getElementById('editPrice').value = product.price;
    document.getElementById('editDiscount').value = product.discount || 0;
    document.getElementById('editStock').value = product.stock;
    document.getElementById('editFeatures').value = product.features;
    document.getElementById('editWarranty').value = product.warranty;

    const editProductModal = document.getElementById('editProductModal');
    if (editProductModal) {
        editProductModal.classList.add('active');
    }
}

function closeEditProductModal() {
    const editProductModal = document.getElementById('editProductModal');
    if (editProductModal) {
        editProductModal.classList.remove('active');
    }
}

async function handleEditProduct(e) {
    e.preventDefault();

    const productId = document.getElementById('editProductId').value;
    const product = {
        product_id: parseInt(productId),
        p_name: document.getElementById('editProductName').value,
        price: parseFloat(document.getElementById('editPrice').value),
        discount: parseFloat(document.getElementById('editDiscount').value) || 0,
        stock: parseInt(document.getElementById('editStock').value),
        features: document.getElementById('editFeatures').value,
        warranty: document.getElementById('editWarranty').value
    };

    const result = await makeRequest('/api/edit_product', 'POST', product);

    if (result.success) {
        showMessage('message', 'Product updated successfully!', 'success');
        closeEditProductModal();
        showSection('productsSection'); // Refresh and stay on section
    } else {
        showMessage('message', result.message || 'Failed to update product!', 'error');
    }
}

// Add product modal functions
function openAddProductModal() {
    const modal = document.getElementById('addProductModal');
    if (modal) {
        modal.classList.add('active');
        loadCategoryDropdown(); // ensure dropdown has latest categories
    }
}

function closeAddProductModal() {
    const modal = document.getElementById('addProductModal');
    if (modal) {
        modal.classList.remove('active');
        document.getElementById('addProductForm').reset();
    }
}

// Category Management Functions
async function loadCategories() {
    const result = await makeRequest('/api/categories_with_count', 'GET');

    if (result.success) {
        displayCategories(result.categories);
        loadCategoryDropdown(); // Also update the dropdown in add product form
    } else {
        showMessage('message', result.message || 'Failed to load categories!', 'error');
    }
}

function loadCategoryDropdown() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;

    // Clear existing options except the first one
    categorySelect.innerHTML = '<option value="">Select a category</option>';

    // Add categories
    makeRequest('/api/categories', 'GET').then(result => {
        if (result.success) {
            result.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                categorySelect.appendChild(option);
            });
        }
    });
}

function displayCategories(categories) {
    const categoriesTableBody = document.getElementById('categoriesTableBody');
    if (!categoriesTableBody) return;
    categoriesTableBody.innerHTML = '';

    if (categories.length === 0) {
        categoriesTableBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No categories found</td></tr>';
        return;
    }

    categories.forEach(category => {
        const row = document.createElement('tr');
        
        const img = document.createElement('img');
        img.src = getImageUrl(category.category_image);
        img.style.width = '50px';
        img.style.height = '50px';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '4px';

        const imgCell = document.createElement('td');
        imgCell.appendChild(img);

        const editImgBtn = document.createElement('button');
        editImgBtn.className = 'btn btn-secondary btn-action';
        editImgBtn.style.width = '100%';
        editImgBtn.textContent = '🖼️ Edit Image';
        editImgBtn.onclick = () => openEditCategoryImageModal(category.category);

        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-action';
        deleteButton.style.width = '100%';
        deleteButton.textContent = '🗑️ Delete';
        deleteButton.onclick = () => deleteCategory(category.category);

        const actionsCell = document.createElement('td');
        actionsCell.style.display = 'flex';
        actionsCell.style.flexDirection = 'column';
        actionsCell.style.gap = '0.5rem';
        actionsCell.style.width = '100%';
        actionsCell.appendChild(editImgBtn);
        actionsCell.appendChild(deleteButton);

        row.appendChild(imgCell);
        row.innerHTML += `
            <td>${category.category}</td>
            <td>${category.product_count}</td>
        `;
        row.appendChild(actionsCell);
        categoriesTableBody.appendChild(row);
    });
}

async function handleAddCategory(e) {
    e.preventDefault();

    const categoryName = document.getElementById('newCategoryName').value.trim();
    const categoryImage = document.getElementById('newCategoryImage').value.trim();

    if (!categoryName) {
        showMessage('message', 'Please enter a category name!', 'error');
        return;
    }

    const result = await makeRequest('/api/add_category', 'POST', {
        category: categoryName,
        category_image: categoryImage
    });

    if (result.success) {
        showMessage('message', 'Category added successfully!', 'success');
        document.getElementById('newCategoryName').value = '';
        closeAddCategoryModal();
        loadCategories(); // Refresh category list
    } else {
        showMessage('message', result.message || 'Failed to add category!', 'error');
    }
}

async function deleteCategory(categoryName) {
    // Show confirmation modal
    document.getElementById('confirmTitle').textContent = 'Delete Category';
    document.getElementById('confirmMessage').textContent = `Are you sure you want to delete the category "${categoryName}"? This will not delete products, but they will be moved to "Uncategorized".`;
    document.getElementById('confirmModal').classList.add('active');

    // Set up the yes button to perform the delete
    document.getElementById('confirmYesBtn').onclick = async function () {
        closeConfirmModal();

        const result = await makeRequest('/api/delete_category', 'POST', {
            category: categoryName
        });

        if (result.success) {
            showMessage('message', 'Category deleted successfully!', 'success');
            loadCategories(); // Refresh category list
        } else {
            showMessage('message', result.message || 'Failed to delete category!', 'error');
        }
    };
}

function openAddCategoryModal() {
    const modal = document.getElementById('addCategoryModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAddCategoryModal() {
    const modal = document.getElementById('addCategoryModal');
    if (modal) {
        modal.classList.remove('active');
    }
    document.getElementById('newCategoryName').value = '';
    document.getElementById('newCategoryImage').value = '';
}

function openEditCategoryImageModal(categoryName) {
    document.getElementById('editCategoryTargetName').value = categoryName;
    document.getElementById('editCategoryImage').value = '';
    const modal = document.getElementById('editCategoryImageModal');
    if (modal) modal.classList.add('active');
}

function closeEditCategoryImageModal() {
    const modal = document.getElementById('editCategoryImageModal');
    if (modal) modal.classList.remove('active');
}

async function handleEditCategoryImage(e) {
    e.preventDefault();
    const categoryName = document.getElementById('editCategoryTargetName').value;
    const categoryImage = document.getElementById('editCategoryImage').value.trim();

    if (!categoryImage) {
        showMessage('message', 'Please enter an image URL!', 'error');
        return;
    }

    const result = await makeRequest('/api/update_category_image', 'POST', {
        category: categoryName,
        category_image: categoryImage
    });

    if (result.success) {
        showMessage('message', 'Category image updated successfully!', 'success');
        closeEditCategoryImageModal();
        loadCategories();
    } else {
        showMessage('message', result.message || 'Failed to update image!', 'error');
    }
}
async function loadUsers() {
    const result = await makeRequest('/api/get_all_users', 'GET');

    if (result.success) {
        displayUsers(result.users);
    } else {
        showMessage('message', result.message || 'Failed to load users!', 'error');
    }
}

function displayUsers(users) {
    const usersTableBody = document.getElementById('usersTableBody');
    usersTableBody.innerHTML = '';

    if (users.length === 0) {
        usersTableBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No users found</td></tr>';
        return;
    }

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.user_id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
        `;
        usersTableBody.appendChild(row);
    });
}

// Load and display products for editing
async function loadProducts() {
    const result = await makeRequest('/api/products', 'GET');

    if (result.success) {
        displayProductsForEdit(result.products);
    } else {
        showMessage('message', result.message || 'Failed to load products!', 'error');
    }
}

function displayProductsForEdit(products) {
    const productsTableBody = document.getElementById('productsTableBody');
    if (!productsTableBody) return;
    productsTableBody.innerHTML = '';

    if (products.length === 0) {
        productsTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No products found</td></tr>';
        return;
    }

    products.forEach(product => {
        const row = document.createElement('tr');
        // Create the HTML content with proper escaping
        const editButton = document.createElement('button');
        editButton.className = 'btn btn-secondary btn-action';
        editButton.style.width = '100%';
        editButton.textContent = 'Edit';
        editButton.onclick = () => editProduct(
            product.product_id,
            product.p_name,
            product.price,
            product.discount || 0,
            product.stock,
            product.features,
            product.warranty
        );

        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-action';
        deleteButton.style.width = '100%';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => deleteProduct(product.product_id);

        const actionsCell = document.createElement('td');
        actionsCell.style.display = 'flex';
        actionsCell.style.flexDirection = 'column';
        actionsCell.style.gap = '0.5rem';
        actionsCell.style.width = '100%';
        actionsCell.appendChild(editButton);
        actionsCell.appendChild(deleteButton);

        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.p_name}</td>
            <td>₹${parseFloat(product.price).toFixed(2)}</td>
            <td>${product.discount || 0}%</td>
            <td>${product.stock}</td>
        `;
        row.appendChild(actionsCell);
        productsTableBody.appendChild(row);
    });
}

function editProduct(id, name, price, discount, stock, features, warranty) {
    openEditProductModal(id, { p_name: name, price: price, discount: discount, stock: stock, features: features, warranty: warranty });
}

async function deleteProduct(productId) {
    // Show confirmation modal
    document.getElementById('confirmTitle').textContent = 'Delete Product';
    document.getElementById('confirmMessage').textContent = 'Are you sure you want to delete this product?';
    document.getElementById('confirmModal').classList.add('active');

    // Set up the yes button to perform the delete
    document.getElementById('confirmYesBtn').onclick = async function () {
        closeConfirmModal();

        const result = await makeRequest('/api/delete_product', 'POST', {
            product_id: productId
        });

        if (result.success) {
            showMessage('message', 'Product deleted successfully!', 'success');
            // Find and remove the row from the table
            const rows = document.querySelectorAll('#productsTableBody tr');
            rows.forEach(row => {
                const productIdCell = row.querySelector('td:first-child');
                if (productIdCell && productIdCell.textContent === productId.toString()) {
                    row.remove();
                }
            });
        } else {
            showMessage('message', result.message || 'Failed to delete product!', 'error');
        }
    };
}

function closeConfirmModal() {
    const modal = document.getElementById('confirmModal');
    modal.classList.remove('active');
}
