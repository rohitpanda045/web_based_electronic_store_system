import { useEffect, useState } from 'react';
import axios from 'axios';
import { Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Cart = () => {
    const [cartItems, setCartItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const fetchCart = async () => {
        try {
            const response = await axios.get('/api/get_cart');
            if (response.data.success) {
                setCartItems(response.data.cart);
            }
        } catch (error) {
            // if 401, redirect to login
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, []);

    const handleRemove = async (productId) => {
        try {
            await axios.post('/api/remove_from_cart', { product_id: productId });
            fetchCart(); // Refresh cart
        } catch (error) {
            alert('Failed to remove item');
        }
    };

    const handleCheckout = async () => {
        try {
            const response = await axios.post('/api/checkout');
            if (response.data.success) {
                alert(`Order placed successfully! Order ID: ${response.data.order_id}`);
                setCartItems([]);
            }
        } catch (error) {
            alert('Checkout failed: ' + (error.response?.data?.message || error.message));
        }
    };

    const calculateTotal = () => {
        return cartItems.reduce((total, item) => {
            const price = item.discounted_price || item.price;
            return total + (price * item.quantity);
        }, 0);
    };

    if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-2">
                <ShoppingBag /> Your Cart
            </h1>

            {cartItems.length === 0 ? (
                <div className="text-center py-16 bg-white rounded-xl shadow-sm">
                    <ShoppingBag size={64} className="mx-auto text-gray-300 mb-4" />
                    <h2 className="text-xl font-bold text-gray-700 mb-2">Your cart is empty</h2>
                    <p className="text-gray-500 mb-6">Looks like you haven't added anything yet.</p>
                    <Link to="/products" className="bg-blue-600 text-white px-6 py-3 rounded-full font-bold hover:bg-blue-700 transition-colors">
                        Start Shopping
                    </Link>
                </div>
            ) : (
                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Cart Items List */}
                    <div className="lg:w-2/3">
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-6 border-b border-gray-100 hidden md:block">
                                <div className="grid grid-cols-12 gap-4 text-sm font-semibold text-gray-500 uppercase tracking-wider">
                                    <div className="col-span-6">Product</div>
                                    <div className="col-span-2 text-center">Price</div>
                                    <div className="col-span-2 text-center">Quantity</div>
                                    <div className="col-span-2 text-center">Total</div>
                                </div>
                            </div>

                            <div className="divide-y divide-gray-100">
                                {cartItems.map((item) => (
                                    <div key={item.product_id} className="p-6 flex flex-col md:grid md:grid-cols-12 gap-4 items-center">
                                        <div className="col-span-6 flex items-center gap-4 w-full">
                                            <img
                                                src={`/static/images/${item.image}`}
                                                alt={item.p_name}
                                                className="w-20 h-20 object-cover rounded-lg bg-gray-100"
                                                onError={(e) => { e.target.src = 'https://via.placeholder.com/100?text=Product'; }}
                                            />
                                            <div>
                                                <h3 className="font-bold text-gray-800">{item.p_name}</h3>
                                                <button
                                                    onClick={() => handleRemove(item.product_id)}
                                                    className="text-red-500 text-sm flex items-center gap-1 mt-1 hover:text-red-700"
                                                >
                                                    <Trash2 size={14} /> Remove
                                                </button>
                                            </div>
                                        </div>

                                        <div className="col-span-2 text-center font-medium md:text-base">
                                            ₹{item.discounted_price ? item.discounted_price.toFixed(2) : item.price}
                                        </div>

                                        <div className="col-span-2 text-center">
                                            <span className="bg-gray-100 px-3 py-1 rounded-md font-bold">{item.quantity}</span>
                                        </div>

                                        <div className="col-span-2 text-center font-bold text-blue-600">
                                            ₹{((item.discounted_price || item.price) * item.quantity).toFixed(2)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Checkout Summary */}
                    <div className="lg:w-1/3">
                        <div className="bg-white rounded-xl shadow-sm p-6 sticky top-24">
                            <h3 className="text-xl font-bold text-gray-800 mb-6">Order Summary</h3>

                            <div className="space-y-4 mb-6">
                                <div className="flex justify-between text-gray-600">
                                    <span>Subtotal</span>
                                    <span>₹{calculateTotal().toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-600">
                                    <span>Shipping</span>
                                    <span>Free</span>
                                </div>
                                <div className="border-t pt-4 flex justify-between text-lg font-bold text-gray-900">
                                    <span>Total</span>
                                    <span>₹{calculateTotal().toFixed(2)}</span>
                                </div>
                            </div>

                            <button
                                onClick={handleCheckout}
                                className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-200"
                            >
                                Checkout Now <ArrowRight size={18} />
                            </button>

                            <div className="mt-4 text-xs text-gray-500 text-center">
                                Secure Checkout • Free Shipping • Easy Returns
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Cart;
