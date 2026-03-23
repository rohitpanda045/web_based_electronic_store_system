import { useEffect, useState } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

const Products = () => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchParams, setSearchParams] = useSearchParams();
    const currentCategory = searchParams.get('category') || '';

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Fetch categories for filter
                const catResponse = await axios.get('/api/categories');
                if (catResponse.data.success) {
                    setCategories(catResponse.data.categories);
                }

                // Fetch products
                const prodUrl = currentCategory
                    ? `/api/products?category=${currentCategory}`
                    : '/api/products';
                const prodResponse = await axios.get(prodUrl);
                if (prodResponse.data.success) {
                    setProducts(prodResponse.data.products);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [currentCategory]);

    const handleCategoryChange = (category) => {
        if (category) {
            setSearchParams({ category });
        } else {
            setSearchParams({});
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    {currentCategory ? `${currentCategory} Products` : 'All Products'}
                </h1>

                {/* Category Filter */}
                <div className="mt-4 md:mt-0 overflow-x-auto pb-2 md:pb-0 w-full md:w-auto">
                    <div className="flex space-x-2">
                        <button
                            onClick={() => handleCategoryChange('')}
                            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${!currentCategory
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                                }`}
                        >
                            All
                        </button>
                        {categories.map((cat) => (
                            <button
                                key={cat}
                                onClick={() => handleCategoryChange(cat)}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${currentCategory === cat
                                        ? 'bg-blue-600 text-white shadow-md'
                                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                                    }`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center py-20">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            ) : (
                <>
                    {products.length === 0 ? (
                        <div className="text-center py-20 text-gray-500">
                            <p className="text-xl">No products found in this category.</p>
                            <button
                                onClick={() => handleCategoryChange('')}
                                className="mt-4 text-blue-600 hover:underline"
                            >
                                View all products
                            </button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {products.map((product) => (
                                <ProductCard key={product.product_id} product={product} />
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Products;
