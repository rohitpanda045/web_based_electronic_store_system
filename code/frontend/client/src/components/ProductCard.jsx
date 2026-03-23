import { ShoppingCart, Heart, Eye, Cpu } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ProductCard = ({ product }) => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const handleAddToCart = async (e) => {
        e.preventDefault();
        if (!user) {
            navigate('/login');
            return;
        }
        try {
            const response = await axios.post('/api/add_to_cart', {
                product_id: product.product_id,
                quantity: 1,
                amount: product.price
            });
            if (response.data.success) {
                // Could show a toast here - for now alert is fine
                alert('UNIT ACQUIRED');
            }
        } catch (error) {
            console.error('Failed to add to cart', error);
        }
    };

    return (
        <div className="group relative bg-[#0a0a0a] border border-white/10 overflow-hidden flex flex-col h-full hover:border-neon-green/50 transition-all duration-300 shadow-lg hover:shadow-[0_0_15px_rgba(204,255,0,0.1)]">
            {/* Corner Accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-neon-green opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-neon-green opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-neon-green opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-neon-green opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <div className="relative pt-[100%] overflow-hidden bg-[#151515]">
                <img
                    src={`/static/images/${product.image}`}
                    alt={product.p_name}
                    className="absolute top-0 left-0 w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500 opacity-80 group-hover:opacity-100"
                    onError={(e) => { e.target.src = 'https://via.placeholder.com/300?text=Product'; }}
                />
                {/* Overlay Grid */}
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/diagmonds-light.png')] opacity-10 pointer-events-none"></div>

                {product.discount > 0 && (
                    <div className="absolute top-2 left-0 bg-neon-green text-black text-xs font-bold px-3 py-1 skew-x-[-10deg] shadow-[0_0_10px_rgba(204,255,0,0.4)]">
                        <span className="skew-x-[10deg] inline-block font-rajdhani tracking-wider">-{product.discount}% OFF</span>
                    </div>
                )}

                {/* Quick Actions Overlay */}
                <div className="absolute top-2 right-2 flex flex-col gap-2 translate-x-10 group-hover:translate-x-0 transition-transform duration-300">
                    <button className="bg-black/80 text-neon-green border border-neon-green/30 p-2 hover:bg-neon-green hover:text-black transition-colors" title="Add to Wishlist">
                        <Heart size={16} />
                    </button>
                    <button className="bg-black/80 text-neon-blue border border-neon-blue/30 p-2 hover:bg-neon-blue hover:text-black transition-colors" title="Quick View">
                        <Eye size={16} />
                    </button>
                </div>
            </div>

            <div className="p-5 flex flex-col flex-grow relative bg-[#0d0d0d] border-t border-white/5">
                <div className="text-[10px] font-bold text-neon-green uppercase tracking-[0.2em] mb-2 flex items-center gap-1">
                    <Cpu size={10} /> {product.category}
                </div>
                <h3 className="text-white font-bold font-orbitron text-lg mb-1 leading-tight group-hover:text-neon-green transition-colors line-clamp-1 decoration-neon-green/30" title={product.p_name}>
                    {product.p_name}
                </h3>
                <p className="text-gray-500 text-xs font-mono mb-4 line-clamp-2 flex-grow border-l border-white/10 pl-2" title={product.features}>{product.features}</p>

                <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                    <div className="flex flex-col">
                        {product.discount > 0 ? (
                            <>
                                <span className="text-gray-500 text-xs line-through font-mono">₹{product.price}</span>
                                <span className="text-xl font-bold font-orbitron text-white">
                                    ₹{(product.price - (product.price * product.discount / 100)).toFixed(0)}
                                </span>
                            </>
                        ) : (
                            <span className="text-xl font-bold font-orbitron text-white">₹{product.price}</span>
                        )}
                    </div>

                    <button
                        onClick={handleAddToCart}
                        className="group/btn relative overflow-hidden bg-white/5 border border-white/20 text-white p-2 px-3 hover:border-neon-green hover:text-neon-green transition-all skew-x-[-10deg]"
                    >
                        <div className="skew-x-[10deg] flex items-center gap-2">
                            <span className="text-xs font-bold tracking-wider">ADD</span>
                            <ShoppingCart size={16} />
                        </div>
                        <div className="absolute inset-0 bg-neon-green/10 transform -translate-x-full group-hover/btn:translate-x-0 transition-transform duration-300"></div>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
