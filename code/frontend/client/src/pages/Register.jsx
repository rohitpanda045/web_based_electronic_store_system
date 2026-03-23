import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { User, Lock, Mail, Phone, MapPin, ArrowRight, AlertTriangle } from 'lucide-react';

const Register = () => {
    const [formData, setFormData] = useState({
        user_id: '',
        email: '',
        name: '',
        phone: '',
        address: '',
        password: ''
    });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await axios.post('/api/register', formData);
            if (response.data.success) {
                alert('Registration successful! Please login.');
                navigate('/login');
            } else {
                setError(response.data.message);
            }
        } catch (error) {
            setError(error.response?.data?.message || 'Registration failed');
        }
    };

    const InputField = ({ label, icon: Icon, type = "text", name, placeholder }) => (
        <div className="group">
            <label className="block text-neon-green text-xs font-bold tracking-widest mb-1 uppercase">{label}</label>
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500 group-focus-within:text-neon-green transition-colors">
                    <Icon size={16} />
                </div>
                <input
                    type={type}
                    name={name}
                    required
                    className="w-full pl-9 pr-3 py-2 bg-white/5 border border-white/10 text-white focus:outline-none focus:border-neon-green focus:bg-white/10 transition-all font-mono placeholder-gray-600 text-sm"
                    placeholder={placeholder}
                    value={formData[name]}
                    onChange={handleChange}
                />
            </div>
        </div>
    );

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-bg relative overflow-hidden font-rajdhani py-12">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,_var(--tw-gradient-stops))] from-gray-900 via-dark-bg to-black opacity-80"></div>
            <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 mix-blend-overlay"></div>

            {/* Animated Glow */}
            <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-neon-green/5 rounded-full blur-[100px] animate-pulse"></div>

            <div className="max-w-2xl w-full relative z-10 p-1">
                {/* Border Gradient */}
                <div className="absolute inset-0 bg-gradient-to-tr from-neon-green/30 to-purple-500/30 rounded-none transform skew-y-[1deg]"></div>

                <div className="bg-black/90 backdrop-blur-xl border border-white/10 p-8 md:p-10 shadow-2xl relative">
                    <div className="text-center mb-8">
                        <h2 className="text-3xl font-bold font-orbitron text-white mb-2 tracking-wide">ESTABLISH UPLINK</h2>
                        <p className="text-gray-400 text-sm font-mono">CREATE YOUR DIGITAL IDENTITY</p>
                    </div>

                    {error && (
                        <div className="mb-6 bg-red-500/10 border-l-4 border-red-500 p-4 text-red-400 text-sm flex items-center gap-2">
                            <AlertTriangle size={16} />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <InputField label="User ID" icon={User} name="user_id" placeholder="UNIQUE_ID" />
                        <InputField label="Full Designation" icon={User} name="name" placeholder="FULL_NAME" />
                        <InputField label="Contact Channel" icon={Mail} type="email" name="email" placeholder="EMAIL_ADDRESS" />
                        <InputField label="Comms Link" icon={Phone} name="phone" placeholder="PHONE_NUMBER" />
                        <InputField label="Passkey Protocol" icon={Lock} type="password" name="password" placeholder="••••••••" />
                        <InputField label="Base Coordinates" icon={MapPin} name="address" placeholder="PHYSICAL_ADDRESS" />

                        <div className="md:col-span-2 mt-4">
                            <button
                                type="submit"
                                className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-neon-green text-black font-bold font-orbitron tracking-widest hover:bg-white transition-all shadow-[0_0_15px_rgba(204,255,0,0.3)] hover:shadow-[0_0_25px_rgba(255,255,255,0.5)] transform hover:-translate-y-1"
                            >
                                ACTIVATE ACCOUNT <ArrowRight size={18} />
                            </button>
                        </div>
                    </form>

                    <div className="mt-8 text-center border-t border-white/10 pt-6">
                        <p className="text-gray-500 text-sm">
                            ALREADY REGISTERED?{' '}
                            <Link to="/login" className="text-neon-green font-bold hover:text-white transition-colors tracking-wide ml-1">
                                [ ACCESS TERMINAL ]
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
