import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { ArrowRight, Sparkles, Palette, Layers, Zap } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [palettes, setPalettes] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, palettesRes] = await Promise.all([
          axios.get(`${API}/products`),
          axios.get(`${API}/palettes`)
        ]);
        setProducts(productsRes.data.slice(0, 6));
        setPalettes(palettesRes.data.slice(0, 4));
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section - Bento Grid */}
      <section className="max-w-7xl mx-auto px-4 md:px-8 py-12 md:py-24">
        <div className="bento-grid">
          {/* Main Hero */}
          <div className="md:col-span-8 bg-black text-white p-8 md:p-12 border-2 border-black animate-slide-up">
            <span className="caption text-[#CCFF00] mb-4 block">Product Design Platform</span>
            <h1 className="heading-xl text-white mb-6">
              CREATE<br />
              <span className="text-[#CCFF00]">ICONIC</span><br />
              DESIGNS
            </h1>
            <p className="body-text text-gray-300 max-w-xl mb-8">
              Upload your designs, customize products, and get AI-powered fashion advice. 
              Build your brand with the vision of Calvin Klein and the innovation of Nike.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/studio"
                className="btn-accent inline-flex items-center gap-2"
                data-testid="hero-start-designing-btn"
              >
                Start Designing <ArrowRight size={18} />
              </Link>
              <Link
                to="/advisor"
                className="btn-secondary bg-transparent text-white border-white hover:bg-white hover:text-black inline-flex items-center gap-2"
                data-testid="hero-ai-advisor-btn"
              >
                <Sparkles size={18} /> AI Fashion Advisor
              </Link>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="md:col-span-4 grid gap-4 md:gap-6">
            <div className="bg-[#CCFF00] p-6 border-2 border-black hard-shadow animate-slide-up stagger-1">
              <Layers className="mb-3" size={32} />
              <h3 className="heading-md mb-2">8+ Products</h3>
              <p className="text-sm">T-shirts, hoodies, shoes, bags & more</p>
            </div>
            <div className="bg-[#FF0099] text-white p-6 border-2 border-black hard-shadow animate-slide-up stagger-2">
              <Palette className="mb-3" size={32} />
              <h3 className="heading-md mb-2">Color Library</h3>
              <p className="text-sm">10+ curated palettes & patterns</p>
            </div>
            <div className="bg-[#00FFFF] p-6 border-2 border-black hard-shadow animate-slide-up stagger-3">
              <Zap className="mb-3" size={32} />
              <h3 className="heading-md mb-2">3 AI Models</h3>
              <p className="text-sm">GPT-5.2, Claude & Gemini advisors</p>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="bg-[#F5F5F5] border-y-2 border-black py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-end justify-between mb-12">
            <div>
              <span className="caption text-gray-500 mb-2 block">Customize</span>
              <h2 className="heading-lg">PRODUCTS</h2>
            </div>
            <Link 
              to="/products" 
              className="btn-primary"
              data-testid="view-all-products-btn"
            >
              View All <ArrowRight size={16} className="ml-2" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {products.map((product, index) => (
              <Link
                key={product.id}
                to={`/studio/${product.slug}`}
                className="product-card animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
                data-testid={`product-card-${product.slug}`}
              >
                <div className="aspect-square bg-white overflow-hidden">
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-4 border-t-2 border-black">
                  <h3 className="heading-md">{product.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                  <div className="flex items-center gap-2 mt-3">
                    <span className="caption bg-[#CCFF00] px-2 py-1 border border-black">
                      {product.design_zones?.length || 0} zones
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Color Palettes Preview */}
      <section className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-end justify-between mb-12">
            <div>
              <span className="caption text-gray-500 mb-2 block">Explore</span>
              <h2 className="heading-lg">COLOR PALETTES</h2>
            </div>
            <Link 
              to="/colors" 
              className="btn-secondary"
              data-testid="view-all-colors-btn"
            >
              View All <ArrowRight size={16} className="ml-2" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {palettes.map((palette, index) => (
              <div 
                key={palette.id} 
                className="card-brutal animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
                data-testid={`palette-${palette.id}`}
              >
                <h3 className="heading-md mb-4">{palette.name}</h3>
                <div className="flex gap-2 mb-3">
                  {palette.colors.map((color, i) => (
                    <div
                      key={i}
                      className="swatch flex-1 aspect-square"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
                <span className="caption text-gray-500">{palette.category}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Advisor CTA */}
      <section className="bg-black text-white py-16 md:py-24 border-y-2 border-black">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <span className="caption text-[#CCFF00] mb-4 block">AI-Powered</span>
              <h2 className="heading-lg text-white mb-6">
                YOUR PERSONAL<br />
                <span className="text-[#FF0099]">FASHION GURU</span>
              </h2>
              <p className="body-text text-gray-300 mb-8">
                Get expert advice from 3 AI models trained on fashion trends. 
                Upload JSON metadata to keep your advisor updated with the latest trends.
                You make the final call—they just help you shine.
              </p>
              <Link 
                to="/advisor" 
                className="btn-accent inline-flex items-center gap-2"
                data-testid="cta-ai-advisor-btn"
              >
                <Sparkles size={18} /> Chat with AI Advisor
              </Link>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-[#10A37F] p-4 border-2 border-white text-center">
                <span className="text-2xl font-bold">GPT</span>
                <p className="text-xs mt-1">5.2</p>
              </div>
              <div className="bg-[#D97757] p-4 border-2 border-white text-center">
                <span className="text-2xl font-bold">Claude</span>
                <p className="text-xs mt-1">Sonnet</p>
              </div>
              <div className="bg-[#4285F4] p-4 border-2 border-white text-center">
                <span className="text-2xl font-bold">Gemini</span>
                <p className="text-xs mt-1">3 Flash</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t-2 border-black py-8">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-black flex items-center justify-center">
                <span className="text-[#CCFF00] font-bold" style={{ fontFamily: 'Syne' }}>DS</span>
              </div>
              <span className="font-bold">Design Studio</span>
            </div>
            <p className="text-sm text-gray-500">
              Build iconic designs with AI-powered fashion advice
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
