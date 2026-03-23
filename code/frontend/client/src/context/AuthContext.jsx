import { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in (could be enhanced with a dedicated /api/me endpoint, 
        // but for now we might rely on session cookie and local state or add a verify endpoint)
        // Since the original app uses server-side sessions, we need an endpoint to check auth status.
        // For this migration, we'll assume the user needs to login again or we add a check route.
        // Let's implement a simple check mechanism or just rely on state persist if implemented.
        // For now, start with null and let login set it.
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = async (userId, password) => {
        try {
            const response = await axios.post('/api/login', { user_id: userId, password });
            if (response.data.success) {
                const userData = { user_id: userId };
                setUser(userData);
                localStorage.setItem('user', JSON.stringify(userData));
                return { success: true };
            }
            return { success: false, message: response.data.message };
        } catch (error) {
            return { success: false, message: error.response?.data?.message || 'Login failed' };
        }
    };

    const register = async (userData) => {
        try {
            const response = await axios.post('/api/register', userData);
            return response.data;
        } catch (error) {
            return { success: false, message: error.response?.data?.message || 'Registration failed' };
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        axios.get('/logout').catch(() => { }); // Optional: call backend logout if exists
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
