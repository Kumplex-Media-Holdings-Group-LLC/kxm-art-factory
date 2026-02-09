import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X, Palette, Layers, MessageSquare, TrendingUp, Home, PenTool } from "lucide-react";

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/products", label: "Products", icon: Layers },
    { path: "/studio", label: "Design Studio", icon: PenTool },
    { path: "/colors", label: "Colors", icon: Palette },
    { path: "/advisor", label: "AI Advisor", icon: MessageSquare },
    { path: "/trends", label: "Trends", icon: TrendingUp },
  ];

  const isActive = (path) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="sticky top-0 z-50 bg-white border-b-2 border-black">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-2"
            data-testid="navbar-logo"
          >
            <div className="w-10 h-10 bg-black flex items-center justify-center">
              <span className="text-[#CCFF00] font-bold text-xl" style={{ fontFamily: 'Syne' }}>DS</span>
            </div>
            <span className="hidden sm:block text-xl font-extrabold uppercase tracking-tight" style={{ fontFamily: 'Syne' }}>
              Design Studio
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-bold border-2 transition-colors duration-200 ${
                  isActive(item.path)
                    ? "bg-[#CCFF00] text-black border-black"
                    : "bg-white text-black border-transparent hover:border-black"
                }`}
              >
                <item.icon size={16} />
                {item.label}
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 border-2 border-black"
            data-testid="mobile-menu-btn"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden border-t-2 border-black bg-white">
          {navItems.map((item, index) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              data-testid={`mobile-nav-${item.label.toLowerCase().replace(' ', '-')}`}
              className={`flex items-center gap-3 px-4 py-3 text-sm font-bold border-b border-gray-200 ${
                isActive(item.path)
                  ? "bg-[#CCFF00] text-black"
                  : "bg-white text-black hover:bg-[#F5F5F5]"
              }`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <item.icon size={18} />
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
