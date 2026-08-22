import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PageShell } from "../components/layout/PageShell";
import { PageHeader } from "../components/ui/PageHeader";
import { TechCard } from "../components/ui/TechCard";
import { getTechnologies } from "../services/content";
import { type Technology, type TechCategory } from "../types/tech";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { usePrefersReducedMotion } from "../hooks/useReducedMotion";

const CATEGORIES: { id: TechCategory; label: string }[] = [
  { id: "backend", label: "Backend" },
  { id: "frontend", label: "Frontend" },
  { id: "database", label: "Database" },
  { id: "deployment", label: "Cloud / Deployment" },
  { id: "tools", label: "Tools" },
];

export const Stack = () => {
  const [items, setItems] = useState<Technology[]>([]);
  const reducedMotion = usePrefersReducedMotion();
  useDocumentMeta({
    title: "Stack",
    description: "Technologies used and currently being learned by Atishaya Jain.",
  });

  useEffect(() => {
    void getTechnologies().then(setItems);
  }, []);

  return (
    <PageShell>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          kicker="Tools"
          title="Stack"
          description="Technologies in active use or currently being learned. No proficiency scores."
        />
        <div className="space-y-10">
          {CATEGORIES.map((category) => {
            const categoryItems = items.filter((tech) => tech.category === category.id);
            if (categoryItems.length === 0) return null;

            return (
              <section key={category.id}>
                <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-muted-gray">
                  {category.label}
                </h2>
                <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                  {categoryItems.map((tech) => (
                    <TechCard key={tech.id} tech={tech} />
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </motion.div>
    </PageShell>
  );
};
