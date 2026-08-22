import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PageShell } from "../components/layout/PageShell";
import { ProjectCard } from "../components/projects/ProjectCard";
import { PageHeader } from "../components/ui/PageHeader";
import { getProjects } from "../services/content";
import { type Project } from "../types/project";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { usePrefersReducedMotion } from "../hooks/useReducedMotion";

export const Projects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const reducedMotion = usePrefersReducedMotion();
  useDocumentMeta({
    title: "Projects",
    description: "Selected work and case studies by Atishaya Jain.",
  });

  useEffect(() => {
    void getProjects().then(setProjects);
  }, []);

  const featured = projects
    .filter((project) => project.featured)
    .sort((a, b) => a.order - b.order);
  const more = projects
    .filter((project) => !project.featured)
    .sort((a, b) => a.order - b.order);

  return (
    <PageShell>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          kicker="Work"
          title="Projects"
          description="Projects I've built while learning, experimenting, and pushing deeper into backend and full-stack development."
        />

        {featured.length ? (
          <section className="mb-14">
            <h2 className="mb-5 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Featured
            </h2>
            <div className="grid gap-5 md:grid-cols-2">
              {featured.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </section>
        ) : null}

        {more.length ? (
          <section>
            <h2 className="mb-5 text-[11px] font-bold uppercase tracking-[0.2em] text-muted-gray">
              More work
            </h2>
            <div className="grid gap-5 md:grid-cols-2">
              {more.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </section>
        ) : null}
      </motion.div>
    </PageShell>
  );
};
