import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Navbar from "@/components/Navbar";
import HomePage from "@/pages/HomePage";
import DesignStudio from "@/pages/DesignStudio";
import ProductGallery from "@/pages/ProductGallery";
import AIAdvisor from "@/pages/AIAdvisor";
import ColorLibrary from "@/pages/ColorLibrary";
import TrendCenter from "@/pages/TrendCenter";

function App() {
  return (
    <div className="min-h-screen bg-white">
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/studio" element={<DesignStudio />} />
          <Route path="/studio/:productSlug" element={<DesignStudio />} />
          <Route path="/products" element={<ProductGallery />} />
          <Route path="/advisor" element={<AIAdvisor />} />
          <Route path="/colors" element={<ColorLibrary />} />
          <Route path="/trends" element={<TrendCenter />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;
