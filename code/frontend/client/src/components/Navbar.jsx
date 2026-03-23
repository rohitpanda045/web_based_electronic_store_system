import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShoppingCart, Menu, X, LogOut, ChevronDown, User, Search } from 'lucide-react';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/login');
        setIsOpen(false);
    };

    const navLinkClass = (path) => `
    relative px-1 py-2 text-sm font-medium transition-all duration-300 tracking-widest uppercase
    ${location.pathname === path ? 'text-neon-green' : 'text-gray-400 hover:text-white'}
    after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[2px] 
    after:bg-neon-green after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:duration-300
    ${location.pathname === path ? 'after:scale-x-100 after:shadow-[0_0_10px_#ccff00]' : ''}
  `;

    return (
        <nav className={`fixed w-full z-50 transition-all duration-300 border-b border-white/5 ${scrolled ? 'bg-black/80 backdrop-blur-md py-2 shadow-lg shadow-neon-green/5' : 'bg-transparent py-4'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 group">
                        <div className="relative">
                            <div className="absolute inset-0 bg-neon-green blur opacity-20 group-hover:opacity-50 transition-opacity duration-300 rounded-full"></div>
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-neon-green relative z-10 transform group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="text-2xl font-bold font-orbitron tracking-wider text-white group-hover:text-neon-green transition-colors duration-300 drop-shadow-[0_0_5px_rgba(204,255,0,0.3)]">
                            TECH<span className="text-neon-green">MART</span>
                        </span>
                    </Link>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center space-x-8">
                        <Link to="/" className={navLinkClass('/')}>Home</Link>
                        <Link to="/products" className={navLinkClass('/products')}>Products</Link>

                        <div className="h-6 w-px bg-white/10 mx-2"></div>

                        <button className="text-gray-400 hover:text-neon-green transition-colors">
                            <Search size={20} className="hover:drop-shadow-[0_0_8px_#ccff00]" />
                        </button>

                        {user ? (
                            <div className="flex items-center gap-6">
                                <Link to="/cart" className="relative group">
                                    <div className="p-2 text-gray-400 group-hover:text-neon-green transition-colors">
                                        <ShoppingCart size={22} className="group-hover:drop-shadow-[0_0_8px_#ccff00] transition-all" />
                                        {/* Badge */}
                                        <span className="absolute top-0 right-0 h-2 w-2 bg-neon-green rounded-full shadow-[0_0_5px_#ccff00]"></span>
                                    </div>
                                </Link>

                                <div className="relative group">
                                    <button className="flex items-center gap-2 text-gray-300 hover:text-white font-medium transition-colors border border-white/10 rounded-full pl-1 pr-3 py-1 hover:border-neon-green/50 hover:bg-white/5">
                                        <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-gray-800 to-black text-neon-green border border-neon-green/30 flex items-center justify-center text-xs font-bold font-orbitron">
                                            {user.user_id ? user.user_id[0].toUpperCase() : 'U'}
                                        </div>
                                        <span className="text-sm tracking-wide font-rajdhani">{user.user_id}</span>
                                        <ChevronDown size={14} className="text-neon-green" />
                                    </button>

                                    {/* Dropdown */}
                                    <div className="absolute right-0 mt-2 w-48 bg-[#0a0a0a] border border-white/10 rounded-none shadow-[0_0_20px_rgba(0,0,0,0.8)] py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 backdrop-blur-xl">
                                        <Link to="/cart" className="block px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-neon-green border-b border-white/5">Your Cart</Link>
                                        <button onClick={handleLogout} className="w-full text-left px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-2 transition-colors">
                                            <LogOut size={16} /> <span className="uppercase tracking-wider text-xs font-bold">Disconnect</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center gap-4">
                                <Link to="/login" className="text-gray-300 hover:text-white font-medium transition-colors uppercase text-sm tracking-wider">Log in</Link>
                                <Link to="/register" className="px-6 py-2 bg-neon-green/10 text-neon-green border border-neon-green/50 hover:bg-neon-green hover:text-black transition-all duration-300 uppercase text-xs font-bold tracking-widest shadow-[0_0_10px_rgba(204,255,0,0.2)] hover:shadow-[0_0_20px_rgba(204,255,0,0.6)] skew-x-[-10deg]">
                                    <span className="skew-x-[10deg] inline-block">Join Link</span>
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="text-gray-300 hover:text-neon-green focus:outline-none p-2"
                        >
                            {isOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu */}
            <div className={`md:hidden absolute w-full bg-black/95 border-b border-white/10 backdrop-blur-xl transition-all duration-300 origin-top ${isOpen ? 'opacity-100 scale-y-100' : 'opacity-0 scale-y-0 h-0'}`}>
                <div className="px-4 pt-4 pb-8 space-y-2 font-rajdhani">
                    <Link to="/" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-neon-green hover:bg-white/5 border-l-2 border-transparent hover:border-neon-green transition-all">Home</Link>
                    <Link to="/products" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-neon-green hover:bg-white/5 border-l-2 border-transparent hover:border-neon-green transition-all">Products</Link>
                    {user ? (
                        <>
                            <Link to="/cart" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-neon-green hover:bg-white/5 border-l-2 border-transparent hover:border-neon-green transition-all">My Cart</Link>
                            <button onClick={handleLogout} className="w-full text-left block px-4 py-3 text-lg font-medium text-red-500 hover:bg-white/5 transition-all">TERMINATE SESSION</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-white">Log In</Link>
                            <Link to="/register" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-neon-green bg-white/5">Initialize Account</Link>
                        </>
                    )}
                    <Link to="/admin/login" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-sm text-gray-600 mt-4 uppercase tracking-widest">Admin Access</Link>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
