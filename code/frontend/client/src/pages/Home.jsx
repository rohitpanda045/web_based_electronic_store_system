import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { ArrowRight, Zap, Shield, Truck, Cpu } from 'lucide-react';

const Home = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await axios.get('/api/categories_with_count');
                if (response.data.success) {
                    setCategories(response.data.categories);
                }
            } catch (error) {
                console.error('Error fetching categories:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchCategories();
    }, []);

    return (
        <div className="flex flex-col min-h-screen font-rajdhani bg-dark-bg text-gray-200">
            {/* Hero Section */}
            <div className="relative overflow-hidden min-h-screen flex items-center">
                {/* Background Effects */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-dark-bg to-black opacity-80 z-0"></div>
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-neon-green/10 rounded-full blur-[100px] animate-pulse"></div>
                <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-neon-blue/10 rounded-full blur-[100px] animate-pulse"></div>

                {/* Grid Pattern */}
                <div className="absolute inset-0 z-0" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full pt-20">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-12">
                        <div className="md:w-1/2 space-y-8">
                            <div className="inline-block px-4 py-1.5 border border-neon-green/30 bg-neon-green/5 text-neon-green rounded-none skew-x-[-10deg] text-sm font-bold tracking-widest animate-fade-in-up shadow-[0_0_10px_rgba(204,255,0,0.1)]">
                                <span className="skew-x-[10deg] inline-block">SYSTEM: ONLINE_READY v2.0</span>
                            </div>
                            <h1 className="text-6xl md:text-8xl font-black font-orbitron text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-500 leading-tight tracking-tighter drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">
                                REAL-TIME <br />
                                <span className="text-neon-green drop-shadow-[0_0_15px_rgba(204,255,0,0.6)]">SHOPPING</span>
                            </h1>
                            <p className="text-xl text-gray-400 max-w-lg leading-relaxed border-l-2 border-neon-green pl-6">
                                Upgrade your existence with next-gen hardware. High-performance gear for total digital dominance.
                            </p>
                            <div className="flex gap-6 pt-4">
                                <Link to="/login" className="relative group overflow-hidden px-8 py-4 bg-glass-dark border border-white/20 text-white font-bold text-lg hover:border-white/50 transition-all skew-x-[-10deg]">
                                    <span className="absolute inset-0 w-full h-full bg-white/10 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></span>
                                    <span className="skew-x-[10deg] inline-block">SECURE LOGIN</span>
                                </Link>
                                <Link to="/register" className="relative group px-8 py-4 bg-neon-green text-black font-bold text-lg hover:bg-white hover:text-black transition-all shadow-[0_0_20px_rgba(204,255,0,0.4)] hover:shadow-[0_0_30px_rgba(255,255,255,0.6)] skew-x-[-10deg]">
                                    <span className="skew-x-[10deg] inline-block flex items-center gap-2">
                                        ACTIVATE ACCOUNT <ArrowRight size={20} />
                                    </span>
                                </Link>
                            </div>
                        </div>

                        {/* Hero Visual */}
                        <div className="md:w-1/2 relative md:h-[600px] flex items-center justify-center">
                            <div className="relative z-10 w-full max-w-sm">
                                <div className="aspect-[3/4] rounded-2xl bg-gradient-to-br from-gray-800 to-black border border-white/10 relative overflow-hidden group">
                                    {/* Placeholder for futuristic modal */}
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <Cpu size={120} className="text-neon-green opacity-50 animate-pulse" />
                                    </div>
                                    <div className="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-black via-black/80 to-transparent">
                                        <div className="text-neon-green text-xs font-bold tracking-widest mb-1">FEATURED ITEM</div>
                                        <div className="text-2xl font-orbitron font-bold text-white mb-2">CYBER JACKET V9</div>
                                        <div className="flex justify-between items-end">
                                            <div className="text-gray-400 text-sm">Ballistic Weave / Smart Connectivity</div>
                                            <div className="text-xl font-bold text-white">$299.99</div>
                                        </div>
                                    </div>
                                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-neon-green to-transparent opacity-50 animate-scan"></div>
                                </div>
                                {/* Floating Elements */}
                                <div className="absolute -top-10 -right-10 w-24 h-24 bg-dark-bg border border-neon-green/30 rounded-lg p-2 flex items-center justify-center animate-float shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                                    <div className="text-center">
                                        <div className="text-neon-green font-bold text-xl">98%</div>
                                        <div className="text-[10px] text-gray-500 uppercase">Efficiency</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Stripe */}
            <div className="bg-black/50 border-y border-white/5 backdrop-blur-sm py-12 relative z-20">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { icon: Shield, title: "ENCRYPTED TRANSACTIONS", sub: "256-bit Protection" },
                            { icon: Truck, title: "HYPER DELIVERY", sub: "Global Logistics" },
                            { icon: Zap, title: "ENERGY OPTIMIZED", sub: "Eco-Friendly Tech" },
                            { icon: Cpu, title: "AI POWERED", sub: "Smart Recommendations" }
                        ].map((feature, i) => (
                            <div key={i} className="flex items-center gap-4 p-4 rounded-none border border-transparent hover:border-white/10 hover:bg-white/5 transition-all group">
                                <div className="p-3 bg-white/5 text-neon-green rounded-none group-hover:bg-neon-green group-hover:text-black transition-colors shadow-[0_0_10px_rgba(204,255,0,0.1)]">
                                    <feature.icon size={24} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-200 font-orbitron text-sm">{feature.title}</h3>
                                    <p className="text-xs text-gray-500 uppercase tracking-wider">{feature.sub}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Categories Section */}
            <div className="max-w-7xl mx-auto px-4 py-24 relative z-10">
                <div className="flex justify-between items-end mb-16">
                    <div>
                        <h2 className="text-4xl md:text-5xl font-bold font-orbitron text-white mb-2">
                            SECTOR <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-green to-emerald-500">CATEGORIES</span>
                        </h2>
                        <div className="h-1 w-24 bg-neon-green rounded-full shadow-[0_0_10px_#ccff00]"></div>
                    </div>
                    <Link to="/products" className="hidden md:flex items-center gap-2 text-neon-green hover:text-white transition-colors uppercase font-bold tracking-widest text-sm">
                        View All Sectors <ArrowRight size={16} />
                    </Link>
                </div>

                {loading ? (
                    <div className="flex justify-center h-64 items-center">
                        <div className="relative w-16 h-16">
                            <div className="absolute inset-0 border-4 border-gray-800 rounded-full"></div>
                            <div className="absolute inset-0 border-4 border-neon-green rounded-full border-t-transparent animate-spin"></div>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                        {categories.map((cat, index) => (
                            <Link to={`/products?category=${cat.category}`} key={index} className="group relative overflow-hidden rounded-none border border-white/10 hover:border-neon-green/50 transition-all duration-500 bg-black/40 h-80 block hover:-translate-y-2">
                                <div className="absolute inset-0 bg-gray-900 overflow-hidden">
                                    <img
                                        src={`/static/images/${cat.category_image}`}
                                        alt={cat.category}
                                        className="w-full h-full object-cover opacity-60 group-hover:opacity-40 transition-opacity duration-500 grayscale group-hover:grayscale-0"
                                        onError={(e) => { e.target.src = 'https://via.placeholder.com/600x400?text=Category'; }}
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent"></div>

                                    {/* Digital overlay effect */}
                                    <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10 mix-blend-overlay"></div>
                                </div>

                                <div className="absolute inset-0 p-8 flex flex-col justify-between">
                                    <div className="flex justify-between items-start">
                                        <span className="text-neon-green text-xs font-bold border border-neon-green/30 px-2 py-1 bg-black/50 backdrop-blur-md">0{index + 1}</span>
                                        <ArrowRight className="text-gray-500 group-hover:text-neon-green transform -translate-x-4 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all duration-300" />
                                    </div>

                                    <div>
                                        <h3 className="text-white text-3xl font-orbitron font-bold mb-2 uppercase tracking-wide group-hover:text-neon-green transition-colors">{cat.category}</h3>
                                        <div className="w-full h-px bg-white/20 group-hover:bg-neon-green/50 transition-colors mb-4"></div>
                                        <span className="text-gray-400 text-sm font-mono">
                      // {cat.product_count} UNITS DETECTED
                                        </span>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            {/* Newsletter / CTA */}
            <div className="relative py-24 px-4 overflow-hidden">
                <div className="absolute inset-0 bg-neon-green/5"></div>
                <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-neon-green to-transparent opacity-50"></div>

                <div className="max-w-4xl mx-auto relative z-10 text-center">
                    <h2 className="text-4xl font-orbitron font-bold text-white mb-6">INITIATE SUBSCRIPTION</h2>
                    <p className="text-gray-400 mb-10 text-lg">Receive data packets on new hardware drops and system upgrades.</p>

                    <div className="flex flex-col sm:flex-row gap-0 max-w-md mx-auto">
                        <input type="email" placeholder="ENTER_EMAIL_ID" className="px-6 py-4 bg-black border border-white/20 text-white focus:outline-none focus:border-neon-green flex-1 font-mono placeholder-gray-600" />
                        <button className="px-8 py-4 bg-neon-green text-black font-bold font-orbitron hover:bg-white transition-colors border-t sm:border-t-0 sm:border-l border-black">
                            CONNECT
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
