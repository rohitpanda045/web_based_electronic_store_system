// Admin login functionality

document.addEventListener('DOMContentLoaded', function() {
    const adminLoginForm = document.getElementById('adminLoginForm');
    
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', handleAdminLogin);
    }
});

async function handleAdminLogin(e) {
    e.preventDefault();
    
    const admin_id = document.getElementById('adminId').value;
    const password = document.getElementById('password').value;
    
    if (!admin_id || !password) {
        showMessage('message', 'All fields are required!', 'error');
        return;
    }
    
    const result = await makeRequest('/api/admin_login', 'POST', {
        admin_id: admin_id,
        password: password
    });
    
    if (result.success) {
        showMessage('message', 'Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = '/admin';
        }, 2000);
    } else {
        showMessage('message', result.message || 'Login failed!', 'error');
    }
}
