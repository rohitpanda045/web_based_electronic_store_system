import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Trash2, Package, List, LayoutDashboard } from 'lucide-react';

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('orders');
    const [orders, setOrders] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    // Form states
    const [newCategory, setNewCategory] = useState('');
    const [newProduct, setNewProduct] = useState({
        p_name: '',
        price: '',
        stock: '',
        category: '',
        features: '',
        warranty: '',
        image: '', // In a real app, handle file upload
        discount: '0'
    });

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'orders') {
                const response = await axios.get('/api/get_all_orders');
                if (response.data.success) setOrders(response.data.orders);
            } else if (activeTab === 'products' || activeTab === 'categories') {
                const catResponse = await axios.get('/api/categories');
                if (catResponse.data.success) setCategories(catResponse.data.categories);
            }
        } catch (error) {
            console.error('Error fetching data', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddCategory = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/add_category', { category: newCategory });
            alert('Category added');
            setNewCategory('');
            fetchData();
        } catch (error) {
            alert('Failed to add category');
        }
    };

    const handleDeleteCategory = async (category) => {
        if (!window.confirm(`Delete category ${category}? Products will be uncategorized.`)) return;
        try {
            await axios.post('/api/delete_category', { category });
            alert('Category deleted');
            fetchData();
        } catch (error) {
            alert('Failed to delete category');
        }
    };

    const handleAddProduct = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/add_product', newProduct);
            alert('Product added successfully');
            setNewProduct({
                p_name: '', price: '', stock: '', category: '', features: '', warranty: '', image: '', discount: '0'
            });
        } catch (error) {
            alert('Failed to add product');
        }
    };

    return (
        <div className="flex h-screen bg-dark-bg">
            {/* Sidebar */}
            <div className="w-64 bg-charcoal text-white border-r border-gray-700">
                <div className="p-6">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <LayoutDashboard /> Admin
                    </h2>
                </div>
                <nav className="mt-6">
                    <button
                        onClick={() => setActiveTab('orders')}
                        className={`w-full flex items-center px-6 py-3 hover:bg-gray-700/50 transition-colors ${activeTab === 'orders' ? 'bg-gray-700/80 border-l-4 border-neon-green' : ''}`}
                    >
                        <List className="mr-3" size={20} /> Orders
                    </button>
                    <button
                        onClick={() => setActiveTab('products')}
                        className={`w-full flex items-center px-6 py-3 hover:bg-gray-700/50 transition-colors ${activeTab === 'products' ? 'bg-gray-700/80 border-l-4 border-neon-green' : ''}`}
                    >
                        <Package className="mr-3" size={20} /> Add Products
                    </button>
                    <button
                        onClick={() => setActiveTab('categories')}
                        className={`w-full flex items-center px-6 py-3 hover:bg-gray-700/50 transition-colors ${activeTab === 'categories' ? 'bg-gray-700/80 border-l-4 border-neon-green' : ''}`}
                    >
                        <List className="mr-3" size={20} /> Categories
                    </button>
                </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto p-8">
                {activeTab === 'orders' && (
                    <div>
                        <h2 className="text-2xl font-bold mb-6 text-gray-200">Recent Orders</h2>
                        <div className="bg-charcoal rounded-lg shadow-lg border border-gray-700 overflow-hidden">
                            <table className="min-w-full divide-y divide-gray-700">
                                <thead className="bg-gray-800/80">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-neon-green uppercase tracking-wider">Order ID</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-neon-green uppercase tracking-wider">User</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-neon-green uppercase tracking-wider">Date</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-neon-green uppercase tracking-wider">Total</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-700">
                                    {orders.map((order) => (
                                        <tr key={order.order_id} className="hover:bg-gray-800/50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-200">#{order.order_id}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{order.username}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{new Date(order.order_date).toLocaleDateString()}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-neon-green">₹{order.total_amount}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'products' && (
                    <div className="max-w-2xl bg-charcoal p-8 rounded-lg shadow-lg border border-gray-700">
                        <h2 className="text-2xl font-bold mb-6 text-gray-200">Add New Product</h2>
                        <form onSubmit={handleAddProduct} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-neon-green mb-1">Product Name</label>
                                    <input type="text" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                        value={newProduct.p_name} onChange={e => setNewProduct({ ...newProduct, p_name: e.target.value })} required />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neon-green mb-1">Category</label>
                                    <select className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                        value={newProduct.category} onChange={e => setNewProduct({ ...newProduct, category: e.target.value })} required>
                                        <option value="">Select Category</option>
                                        {categories.map(c => <option key={c} value={c}>{c}</option>)}
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-neon-green mb-1">Price</label>
                                    <input type="number" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                        value={newProduct.price} onChange={e => setNewProduct({ ...newProduct, price: e.target.value })} required />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neon-green mb-1">Stock</label>
                                    <input type="number" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                        value={newProduct.stock} onChange={e => setNewProduct({ ...newProduct, stock: e.target.value })} required />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neon-green mb-1">Discount (%)</label>
                                    <input type="number" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                        value={newProduct.discount} onChange={e => setNewProduct({ ...newProduct, discount: e.target.value })} />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-neon-green mb-1">Image Name (in static/images)</label>
                                <input type="text" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                    value={newProduct.image} onChange={e => setNewProduct({ ...newProduct, image: e.target.value })} placeholder="e.g., laptop.jpg" />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-neon-green mb-1">Features</label>
                                <textarea className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green" rows="3"
                                    value={newProduct.features} onChange={e => setNewProduct({ ...newProduct, features: e.target.value })}></textarea>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-neon-green mb-1">Warranty</label>
                                <input type="text" className="block w-full rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                    value={newProduct.warranty} onChange={e => setNewProduct({ ...newProduct, warranty: e.target.value })} />
                            </div>

                            <button type="submit" className="w-full bg-neon-green text-dark-bg font-bold py-2 rounded-lg hover:bg-neon-blue transition-colors">
                                Add Product
                            </button>
                        </form>
                    </div>
                )}

                {activeTab === 'categories' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-charcoal p-6 rounded-lg shadow-lg border border-gray-700">
                            <h3 className="text-lg font-bold mb-4 text-gray-200">Add New Category</h3>
                            <form onSubmit={handleAddCategory} className="flex gap-2">
                                <input
                                    type="text"
                                    value={newCategory}
                                    onChange={(e) => setNewCategory(e.target.value)}
                                    className="flex-1 rounded-md border-2 border-gray-600 bg-dark-bg text-gray-200 p-2 focus:border-neon-green focus:outline-none focus:ring-1 focus:ring-neon-green"
                                    placeholder="Category Name"
                                    required
                                />
                                <button type="submit" className="bg-neon-green text-dark-bg px-4 py-2 rounded-md hover:bg-neon-blue transition-colors font-semibold">
                                    <Plus size={20} />
                                </button>
                            </form>
                        </div>

                        <div className="bg-charcoal p-6 rounded-lg shadow-lg border border-gray-700">
                            <h3 className="text-lg font-bold mb-4 text-gray-200">Manage Categories</h3>
                            <ul className="space-y-2">
                                {categories.map(cat => (
                                    <li key={cat} className="flex justify-between items-center p-3 hover:bg-gray-800/50 rounded border border-gray-700">
                                        <span className="text-gray-200">{cat}</span>
                                        <button onClick={() => handleDeleteCategory(cat)} className="text-red-400 hover:text-red-300 transition-colors">
                                            <Trash2 size={18} />
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
