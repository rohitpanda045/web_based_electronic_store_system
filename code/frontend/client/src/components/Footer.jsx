import { Facebook, Twitter, Instagram, Linkedin, Mail, Phone, MapPin, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="bg-[#050505] text-gray-300 pt-16 pb-8 border-t border-white/5 font-rajdhani relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-neon-green/5 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    {/* Brand */}
                    <div>
                        <Link to="/" className="flex items-center gap-2 mb-4 group">
                            <Zap className="text-neon-green" size={24} />
                            <span className="text-2xl font-bold font-orbitron text-white">TECH<span className="text-neon-green">MART</span></span>
                        </Link>
                        <p className="text-gray-500 leading-relaxed mb-6 text-sm">
                            Supplying high-grade cybernetics and digital logistics for the modern era. Quality assured. secure transactions.
                        </p>
                        <div className="flex gap-4">
                            {[Facebook, Twitter, Instagram, Linkedin].map((Icon, i) => (
                                <a key={i} href="#" className="w-10 h-10 rounded-none border border-white/10 flex items-center justify-center hover:bg-neon-green hover:text-black hover:border-neon-green transition-all duration-300">
                                    <Icon size={18} />
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-lg font-bold mb-6 text-white font-orbitron tracking-wider">SECTORS</h4>
                        <ul className="space-y-3">
                            {['Home', 'Products', 'Cart', 'Sign Up', 'Admin Portal'].map((item, i) => (
                                <li key={i}>
                                    <Link to={item === 'Home' ? '/' : `/${item.toLowerCase().replace(' ', '')}`} className="text-gray-400 hover:text-neon-green transition-colors text-sm hover:translate-x-1 inline-block">
                        // {item}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Customer Service */}
                    <div>
                        <h4 className="text-lg font-bold mb-6 text-white font-orbitron tracking-wider">PROTOCOLS</h4>
                        <ul className="space-y-3">
                            {['Help Center', 'Terms of Service', 'Privacy Policy', 'Returns & Refunds', 'Track Order'].map((item, i) => (
                                <li key={i}>
                                    <a href="#" className="text-gray-400 hover:text-white transition-colors text-sm hover:translate-x-1 inline-block">
                        // {item}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="text-lg font-bold mb-6 text-white font-orbitron tracking-wider">TRANSMISSION</h4>
                        <ul className="space-y-4 text-sm">
                            <li className="flex items-start gap-3 text-gray-400 group">
                                <MapPin size={20} className="text-neon-green mt-1 flex-shrink-0 group-hover:drop-shadow-[0_0_5px_#ccff00]" />
                                <span>123 Tech Avenue, Sector 7<br />Silicon Valley, CA 94025</span>
                            </li>
                            <li className="flex items-center gap-3 text-gray-400 group">
                                <Phone size={20} className="text-neon-green flex-shrink-0 group-hover:drop-shadow-[0_0_5px_#ccff00]" />
                                <span>+1 (555) 123-4567</span>
                            </li>
                            <li className="flex items-center gap-3 text-gray-400 group">
                                <Mail size={20} className="text-neon-green flex-shrink-0 group-hover:drop-shadow-[0_0_5px_#ccff00]" />
                                <span>support@techmart.com</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-gray-600 text-xs font-mono">
                        &copy; {new Date().getFullYear()} TECHMART SYSTEMS. ALL RIGHTS RESERVED.
                    </p>
                    <div className="flex gap-6 text-xs text-gray-500 font-mono">
                        <a href="#" className="hover:text-neon-green transition-colors">PRIVACY_PROTOCOL</a>
                        <a href="#" className="hover:text-neon-green transition-colors">TERMS_OF_USE</a>
                        <a href="#" className="hover:text-neon-green transition-colors">COOKIES</a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
