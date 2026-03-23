import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { User, Lock, ArrowRight, AlertTriangle } from 'lucide-react';

const Login = () => {
    const [userId, setUserId] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const result = await login(userId, password);
        if (result.success) {
            navigate('/');
        } else {
            setError(result.message);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-bg relative overflow-hidden font-rajdhani">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-dark-bg to-black opacity-80"></div>
            <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 mix-blend-overlay"></div>

            {/* Animated Glow */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-neon-green/10 rounded-full blur-[80px] animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-neon-blue/10 rounded-full blur-[80px] animate-pulse animation-delay-2000"></div>

            <div className="max-w-md w-full relative z-10 p-1">
                {/* Border Gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-neon-green/30 to-neon-blue/30 rounded-none transform skew-x-[-2deg]"></div>

                <div className="bg-black/90 backdrop-blur-xl border border-white/10 p-8 shadow-2xl relative">
                    <div className="text-center mb-10">
                        <div className="inline-block p-3 rounded-full bg-neon-green/10 text-neon-green mb-4 border border-neon-green/30 shadow-[0_0_15px_rgba(204,255,0,0.2)]">
                            <User size={32} />
                        </div>
                        <h2 className="text-4xl font-bold font-orbitron text-white mb-2 tracking-wide">SYSTEM ACCESS</h2>
                        <p className="text-gray-400 text-sm font-mono">ENTER CREDENTIALS TO PROCEED</p>
                    </div>

                    {error && (
                        <div className="mb-6 bg-red-500/10 border-l-4 border-red-500 p-4 text-red-400 text-sm flex items-center gap-2">
                            <AlertTriangle size={16} />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="group">
                            <label className="block text-neon-green text-xs font-bold tracking-widest mb-2 uppercase">User Identifier</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500 group-focus-within:text-neon-green transition-colors">
                                    <User size={18} />
                                </div>
                                <input
                                    type="text"
                                    value={userId}
                                    onChange={(e) => setUserId(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 text-white focus:outline-none focus:border-neon-green focus:bg-white/10 transition-all font-mono placeholder-gray-600"
                                    placeholder="USER_ID"
                                    required
                                />
                            </div>
                        </div>

                        <div className="group">
                            <label className="block text-neon-green text-xs font-bold tracking-widest mb-2 uppercase">Passkey</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500 group-focus-within:text-neon-green transition-colors">
                                    <Lock size={18} />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 text-white focus:outline-none focus:border-neon-green focus:bg-white/10 transition-all font-mono placeholder-gray-600"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between text-xs">
                            <label className="flex items-center text-gray-400 hover:text-white cursor-pointer select-none">
                                <input type="checkbox" className="form-checkbox bg-transparent border-gray-600 rounded-sm text-neon-green focus:ring-0 mr-2" />
                                REMEMBER SESSION
                            </label>
                            <a href="#" className="text-gray-400 hover:text-neon-green transition-colors">FORGOT DATA?</a>
                        </div>

                        <button
                            type="submit"
                            className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-neon-green text-black font-bold font-orbitron tracking-widest hover:bg-white transition-all shadow-[0_0_15px_rgba(204,255,0,0.3)] hover:shadow-[0_0_25px_rgba(255,255,255,0.5)] transform hover:-translate-y-1"
                        >
                            INITIATE LOGIN <ArrowRight size={18} />
                        </button>
                    </form>

                    <div className="mt-8 text-center border-t border-white/10 pt-6">
                        <p className="text-gray-500 text-sm">
                            NEW USER DETECTED?{' '}
                            <Link to="/register" className="text-neon-green font-bold hover:text-white transition-colors tracking-wide ml-1">
                                [ CREATE ACCOUNT ]
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
