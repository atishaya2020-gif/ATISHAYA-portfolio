import { useEffect, useState } from "react";
import { Section } from "../layout/Section";
import { TechCard } from "../ui/TechCard";
import { getTechnologies } from "../../services/content";
import { type Technology, type TechCategory } from "../../types/tech";

const CATEGORIES: { id: TechCategory; label: string }[] = [
  { id: "backend", label: "Backend" },
  { id: "frontend", label: "Frontend" },
  { id: "database", label: "Database" },
  { id: "deployment", label: "Cloud / Deployment" },
  { id: "tools", label: "Tools" },
];

export const TechStack = () => {
  const [items, setItems] = useState<Technology[]>([]);

  useEffect(() => {
    void getTechnologies().then(setItems);
  }, []);

  return (
    <Section id="stack" title="TECH STACK">
      <div className="space-y-10">
        {CATEGORIES.map(({ id, label }) => {
          const categoryItems = items.filter((tech) => tech.category === id);
          if (categoryItems.length === 0) return null;

          return (
            <div key={id}>
              <h3 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-muted-gray">
                {label}
              </h3>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {categoryItems.map((tech) => (
                  <TechCard key={tech.id} tech={tech} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Section>
  );
};
