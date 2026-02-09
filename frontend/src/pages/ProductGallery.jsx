import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { ArrowRight, Info } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ProductGallery() {
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loading, setLoading] = useState(true);

  const categories = [
    { id: "all", name: "All Products" },
    { id: "apparel", name: "Apparel", items: ["tshirt", "hoodie"] },
    { id: "accessories", name: "Accessories", items: ["cap", "tote-bag", "backpack"] },
    { id: "footwear", name: "Footwear", items: ["sneakers"] },
    { id: "lifestyle", name: "Lifestyle", items: ["mug", "phone-case"] }
  ];

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API}/products`);
        setProducts(response.data);
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const filteredProducts = selectedCategory === "all" 
    ? products 
    : products.filter(p => {
        const cat = categories.find(c => c.id === selectedCategory);
        return cat?.items?.includes(p.slug);
      });

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <section className="bg-[#CCFF00] border-b-2 border-black py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <span className="caption text-black mb-2 block">Browse & Design</span>
          <h1 className="heading-xl">PRODUCTS</h1>
          <p className="body-text mt-4 max-w-2xl">
            Choose a product to customize. Each product has research-based design zones 
            showing the most impactful placement areas.
          </p>
        </div>
      </section>

      {/* Filter Bar */}
      <section className="border-b-2 border-black py-4 sticky top-16 bg-white z-40">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                data-testid={`filter-${cat.id}`}
                className={`px-4 py-2 text-sm font-bold border-2 whitespace-nowrap transition-colors duration-200 ${
                  selectedCategory === cat.id
                    ? "bg-black text-white border-black"
                    : "bg-white text-black border-black hover:bg-[#F5F5F5]"
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="spinner"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredProducts.map((product, index) => (
                <ProductCard key={product.id} product={product} index={index} />
              ))}
            </div>
          )}

          {!loading && filteredProducts.length === 0 && (
            <div className="text-center py-20">
              <p className="body-text text-gray-500">No products found in this category.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function ProductCard({ product, index }) {
  const [showZones, setShowZones] = useState(false);

  return (
    <div 
      className="product-card animate-slide-up"
      style={{ animationDelay: `${index * 50}ms` }}
      data-testid={`product-gallery-card-${product.slug}`}
    >
      <div className="aspect-square bg-[#F5F5F5] overflow-hidden relative">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
        />
        <button
          onClick={(e) => {
            e.preventDefault();
            setShowZones(!showZones);
          }}
          className="absolute top-3 right-3 p-2 bg-white border-2 border-black hover:bg-[#CCFF00] transition-colors"
          data-testid={`info-btn-${product.slug}`}
        >
          <Info size={16} />
        </button>

        {/* Design Zones Overlay */}
        {showZones && (
          <div className="absolute inset-0 bg-black/80 p-4 flex flex-col justify-center animate-fade-in">
            <h4 className="text-white font-bold mb-3">Design Zones</h4>
            <ul className="space-y-2">
              {product.design_zones?.map((zone, i) => (
                <li key={i} className="text-sm text-white flex items-center gap-2">
                  <span className="w-2 h-2 bg-[#CCFF00]"></span>
                  {zone.name}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="p-4 border-t-2 border-black">
        <h3 className="heading-md text-lg">{product.name}</h3>
        <p className="text-sm text-gray-600 mt-1 line-clamp-2">{product.description}</p>
        
        <div className="flex items-center justify-between mt-4">
          <div className="flex gap-1">
            {product.design_zones?.slice(0, 3).map((_, i) => (
              <span key={i} className="w-3 h-3 bg-[#FF0099] border border-black"></span>
            ))}
          </div>
          <Link
            to={`/studio/${product.slug}`}
            className="inline-flex items-center gap-1 text-sm font-bold hover:text-[#FF0099] transition-colors"
            data-testid={`design-btn-${product.slug}`}
          >
            Design <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
