import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowUpRight, Github } from "lucide-react";
import { PageShell } from "../components/layout/PageShell";
import { ProjectVisual } from "../components/projects/ProjectVisual";
import { getProjectBySlug } from "../services/content";
import { type Project } from "../types/project";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { usePrefersReducedMotion } from "../hooks/useReducedMotion";

const statusLabel: Record<Project["status"], string> = {
  "in-progress": "In progress",
  completed: "Completed",
  archived: "Archived",
};

export const ProjectDetail = () => {
  const { slug } = useParams();
  const [project, setProject] = useState<Project | null | undefined>(undefined);
  const reducedMotion = usePrefersReducedMotion();

  useDocumentMeta({
    title: project?.title ?? "Case study",
    description: project?.shortDescription,
  });

  useEffect(() => {
    let active = true;
    if (slug) {
      void getProjectBySlug(slug).then((project) => {
        if (active) setProject(project);
      });
    }
    return () => {
      active = false;
    };
  }, [slug]);

  if (project === undefined) return null;

  if (!project) {
    return (
      <PageShell>
        <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.22em] text-raging-red">
          Not found
        </p>
        <h1 className="mb-4 text-4xl font-black uppercase tracking-tighter">
          Project missing
        </h1>
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-raging-red"
        >
          <ArrowLeft size={14} />
          Back to projects
        </Link>
      </PageShell>
    );
  }

  const order = project.order.toString().padStart(2, "0");

  return (
    <PageShell>
      <motion.article
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.18em] text-muted-gray">
          {order} / {project.category} / {statusLabel[project.status]}
        </p>
        <h1 className="mb-3 text-4xl font-black uppercase tracking-tighter md:text-6xl">
          {project.title}
        </h1>
        {project.subtitle ? (
          <p className="mb-5 font-mono text-xs font-bold uppercase tracking-[0.2em] text-raging-red">
            {project.subtitle}
          </p>
        ) : null}
        <p className="mb-8 max-w-2xl text-base leading-relaxed text-muted-gray">
          {project.shortDescription}
        </p>

        <div className="mb-10 flex flex-wrap gap-3">
          {project.githubUrl ? (
            <a
              href={project.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-raging-red px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:bg-red-700"
            >
              View GitHub
              <Github size={14} />
            </a>
          ) : null}
          {project.liveUrl ? (
            <a
              href={project.liveUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 border border-white/10 px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:border-raging-red hover:bg-white/5"
            >
              Live demo
              <ArrowUpRight size={14} />
            </a>
          ) : null}
          {project.apiUrl ? (
            <a
              href={project.apiUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 border border-white/10 px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:border-raging-red hover:bg-white/5"
            >
              API
              <ArrowUpRight size={14} />
            </a>
          ) : null}
        </div>

        <div className="mb-12 aspect-[16/8] overflow-hidden border border-white/5">
          {project.image ? (
            <img
              src={project.image}
              alt={`${project.title} preview`}
              className="h-full w-full object-cover"
            />
          ) : (
            <ProjectVisual title={project.title} className="h-full w-full" />
          )}
        </div>

        {project.overview ?? project.fullDescription ? (
          <section className="mb-10">
            <h2 className="mb-3 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Overview
            </h2>
            <p className="max-w-3xl text-base leading-relaxed text-muted-gray">
              {project.overview ?? project.fullDescription}
            </p>
          </section>
        ) : null}

        {project.architecture?.length ? (
          <section className="mb-10 border border-white/5 bg-white/[0.02] p-5 md:p-7">
            <h2 className="mb-5 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Architecture
            </h2>
            <ol className="space-y-4">
              {project.architecture.map((item, index) => (
                <li
                  key={item}
                  className="flex gap-4 text-sm leading-relaxed text-muted-gray"
                >
                  <span className="shrink-0 pt-px font-mono text-xs font-bold text-raging-red">
                    {(index + 1).toString().padStart(2, "0")}
                  </span>
                  <p>{item}</p>
                </li>
              ))}
            </ol>
          </section>
        ) : null}

        {project.features?.length ? (
          <section className="mb-10">
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Key features
            </h2>
            <ul className="grid gap-x-8 gap-y-2 sm:grid-cols-2">
              {project.features.map((feature) => (
                <li
                  key={feature}
                  className="flex items-baseline gap-3 border-b border-white/5 pb-2 text-sm leading-relaxed text-muted-gray"
                >
                  <span className="text-raging-red">{">"}</span>
                  {feature}
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {project.technologies.length ? (
          <section className="mb-12">
            <h2 className="mb-4 text-[11px] font-bold uppercase tracking-[0.2em] text-raging-red">
              Technology stack
            </h2>
            <div className="flex flex-wrap gap-2">
              {project.technologies.map((tech) => (
                <span
                  key={tech}
                  className="border border-white/10 px-2 py-1 font-mono text-[11px] text-white/70"
                >
                  {tech}
                </span>
              ))}
            </div>
          </section>
        ) : null}

        <Link
          to="/projects"
          className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-raging-red"
        >
          <ArrowLeft size={14} />
          Back to projects
        </Link>
      </motion.article>
    </PageShell>
  );
};
