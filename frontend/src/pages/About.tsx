import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PageShell } from "../components/layout/PageShell";
import { PageHeader } from "../components/ui/PageHeader";
import { getProfile } from "../services/content";
import { type Profile } from "../types/profile";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { usePrefersReducedMotion } from "../hooks/useReducedMotion";

export const About = () => {
  const [data, setData] = useState<Profile | null>(null);
  const reducedMotion = usePrefersReducedMotion();
  useDocumentMeta({
    title: "About",
    description:
      "About Atishaya Jain — backend-focused developer studying B.Tech CSE at CGC Landran, currently learning Django REST Framework and API development.",
  });

  useEffect(() => {
    void getProfile().then(setData);
  }, []);

  if (!data) return null;

  return (
    <PageShell>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          kicker="About"
          title={data.name}
          description={data.introduction}
        />

        {data.philosophy ? (
          <blockquote className="mb-12 max-w-3xl border-l-2 border-raging-red pl-5 text-xl font-medium leading-relaxed text-white md:text-2xl">
            &ldquo;{data.philosophy}&rdquo;
          </blockquote>
        ) : null}

        <div className="grid gap-12 md:grid-cols-2">
          <section>
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Education
            </h2>
            <div className="space-y-5">
              {data.education.map((item) => (
                <div key={item.id} className="border-l border-white/10 pl-4">
                  <p className="mb-1 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-gray">
                    {item.label}
                  </p>
                  <h3 className="mb-1 font-bold">{item.title}</h3>
                  <p className="text-sm leading-relaxed text-muted-gray">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Development journey
            </h2>
            <div className="space-y-5">
              {data.journey.map((item) => (
                <div key={item.id} className="border-l border-white/10 pl-4">
                  <p className="mb-1 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-gray">
                    {item.label}
                  </p>
                  <h3 className="mb-1 font-bold">{item.title}</h3>
                  <p className="text-sm leading-relaxed text-muted-gray">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-3">
          <section>
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Current focus
            </h2>
            <ul className="space-y-3 text-sm leading-relaxed text-muted-gray">
              {data.currentFocus.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              What I build
            </h2>
            <ul className="space-y-3 text-sm leading-relaxed text-muted-gray">
              {data.whatIBuild.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Goals
            </h2>
            <ul className="space-y-3 text-sm leading-relaxed text-muted-gray">
              {data.goals.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        </div>
      </motion.div>
    </PageShell>
  );
};
