// Registration page functionality

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
});

async function handleRegistration(e) {
    e.preventDefault();
    
    const user_id = document.getElementById('userId').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    const address = document.getElementById('address').value;
    
    if (password !== confirmPassword) {
        showMessage('message', 'Passwords do not match!', 'error');
        return;
    }
    
    if (!user_id || !username || !email || !password || !address) {
        showMessage('message', 'All fields are required!', 'error');
        return;
    }
    
    const result = await makeRequest('/api/register', 'POST', {
        user_id: user_id,
        username: username,
        email: email,
        password: password,
        address: address
    });
    
    if (result.success) {
        showMessage('message', 'Registration successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } else {
        showMessage('message', result.message || 'Registration failed!', 'error');
    }
}
