// Login page functionality

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const user_id = document.getElementById('userId').value;
    const password = document.getElementById('password').value;
    
    if (!user_id || !password) {
        showMessage('message', 'All fields are required!', 'error');
        return;
    }
    
    const result = await makeRequest('/api/login', 'POST', {
        user_id: user_id,
        password: password
    });
    
    if (result.success) {
        showMessage('message', 'Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = '/products';
        }, 2000);
    } else {
        showMessage('message', result.message || 'Login failed!', 'error');
    }
}
