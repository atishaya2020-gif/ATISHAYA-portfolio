import { Hero } from "../components/hero/Hero";
import { Footer } from "../components/layout/Footer";
import { AboutPreview } from "../components/sections/AboutPreview";
import { Contact } from "../components/sections/Contact";
import { FeaturedProjects } from "../components/sections/FeaturedProjects";
import { TechStack } from "../components/sections/TechStack";
import { useDocumentMeta } from "../hooks/useDocumentMeta";

export const Home = () => {
  useDocumentMeta({ title: "Home" });

  return (
    <>
      <Hero />
      <AboutPreview />
      <FeaturedProjects />
      <TechStack />
      <Contact />
      <Footer />
    </>
  );
};
