import { useState } from "react";
import { Github, Linkedin, Menu, Moon, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { Link, NavLink, useLocation } from "react-router-dom";
import { useScroll } from "../../hooks/useScroll";
import { SITE } from "../../lib/site";

const navLinks = [
  { name: "Home", href: "/" },
  { name: "About", href: "/about" },
  { name: "Projects", href: "/projects" },
  { name: "Stack", href: "/stack" },
  { name: "Contact", href: "/contact" },
];

export const Navbar = () => {
  const isScrolled = useScroll(24);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-near-black/90 backdrop-blur-md py-3 border-b border-white/5"
          : "bg-transparent py-5"
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6">
        <Link
          to="/"
          className="text-sm font-bold tracking-[0.18em] uppercase"
          onClick={closeMenu}
        >
          {SITE.name}
        </Link>

        <div className="hidden items-center gap-7 md:flex">
          {navLinks.map((link) => (
            <NavLink
              key={link.name}
              to={link.href}
              end={link.href === "/"}
              className={({ isActive }) =>
                `text-[11px] font-bold uppercase tracking-[0.18em] transition-colors ${
                  isActive
                    ? "text-raging-red"
                    : "text-muted-gray hover:text-white"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </div>

        <div className="hidden items-center gap-4 text-muted-gray md:flex">
          {SITE.github ? (
            <a
              href={SITE.github}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              className="transition-colors hover:text-raging-red"
            >
              <Github size={16} />
            </a>
          ) : null}
          {SITE.linkedin ? (
            <a
              href={SITE.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
              className="transition-colors hover:text-raging-red"
            >
              <Linkedin size={16} />
            </a>
          ) : null}
          <button
            type="button"
            aria-label="Toggle theme"
            className="transition-colors hover:text-raging-red"
          >
            <Moon size={16} />
          </button>
        </div>

        <button
          type="button"
          className="md:hidden"
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((open) => !open)}
        >
          {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <AnimatePresence>
        {isMenuOpen ? (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-white/5 bg-near-black md:hidden"
          >
            <div className="flex flex-col gap-5 px-6 py-6">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  onClick={closeMenu}
                  className={`text-sm font-bold uppercase tracking-[0.18em] ${
                    location.pathname === link.href ||
                    (link.href !== "/" && location.pathname.startsWith(link.href))
                      ? "text-raging-red"
                      : "text-muted-gray"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </nav>
  );
};
