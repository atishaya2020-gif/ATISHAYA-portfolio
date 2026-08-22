import { type ReactNode } from "react";
import { motion } from "framer-motion";
import { usePrefersReducedMotion } from "../../hooks/useReducedMotion";

interface SectionProps {
  id: string;
  title: string;
  children: ReactNode;
}

export const Section = ({ id, title, children }: SectionProps) => {
  const reducedMotion = usePrefersReducedMotion();

  return (
    <section id={id} className="border-t border-white/5 py-16 md:py-20">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8 flex items-center gap-3">
            <div className="h-px w-7 bg-raging-red" />
            <h2 className="text-[11px] font-bold uppercase tracking-[0.22em] text-raging-red">
              {title}
            </h2>
          </div>
          {children}
        </motion.div>
      </div>
    </section>
  );
};
