import { ArrowRight, Github } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { type Project } from "../../types/project";
import { usePrefersReducedMotion } from "../../hooks/useReducedMotion";
import { ProjectVisual } from "./ProjectVisual";

interface ProjectCardProps {
  project: Project;
}

const statusLabel: Record<Project["status"], string> = {
  "in-progress": "In progress",
  completed: "Completed",
  archived: "Archived",
};

export const ProjectCard = ({ project }: ProjectCardProps) => {
  const reducedMotion = usePrefersReducedMotion();
  const formattedOrder = project.order.toString().padStart(2, "0");

  return (
    <motion.article
      className="group overflow-hidden border border-card-border bg-card-bg transition-colors duration-300 hover:border-raging-red/50"
      whileHover={reducedMotion ? undefined : { y: -4 }}
    >
      <div className="flex items-start justify-between px-5 pt-5 pb-4">
        <div>
          <div className="mb-1 font-mono text-xs font-bold text-raging-red">
            {formattedOrder}
          </div>
          <h3 className="text-2xl font-black tracking-tighter transition-colors group-hover:text-raging-red">
            {project.title}
          </h3>
        </div>
        <span className="border border-white/10 bg-white/5 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-muted-gray">
          {statusLabel[project.status]}
        </span>
      </div>

      <Link
        to={`/projects/${project.slug}`}
        aria-label={`View ${project.title} case study`}
        className="relative block aspect-[16/9] overflow-hidden border-y border-white/5"
      >
        {project.image ? (
          <img
            src={project.image}
            alt={`${project.title} preview`}
            loading="lazy"
            className="h-full w-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="h-full w-full transition-transform duration-500 group-hover:scale-105">
            <ProjectVisual title={project.title} className="h-full w-full" />
          </div>
        )}
        <div className="pointer-events-none absolute inset-0 bg-raging-red/0 transition-colors duration-300 group-hover:bg-raging-red/8" />
        {project.image ? (
          <div className="pointer-events-none absolute left-4 top-4 border border-white/10 bg-black/60 px-2 py-1 font-mono text-[9px] uppercase tracking-[0.2em] text-white/55 backdrop-blur-sm">
            Live preview
          </div>
        ) : null}
      </Link>

      <div className="p-5">
        <p className="mb-5 text-sm leading-relaxed text-muted-gray">
          {project.shortDescription}
        </p>

        <div className="mb-6 flex flex-wrap gap-2">
          {project.technologies.map((tech) => (
            <span
              key={tech}
              className="border border-white/10 px-2 py-1 font-mono text-[11px] text-white/70"
            >
              {tech}
            </span>
          ))}
        </div>

        <div className="flex flex-wrap gap-5 text-[11px] font-bold uppercase tracking-[0.16em]">
          <Link
            to={`/projects/${project.slug}`}
            className="group/link inline-flex items-center gap-2 text-raging-red"
          >
            View case study
            <ArrowRight
              size={13}
              className="transition-transform group-hover/link:translate-x-1"
            />
          </Link>
          {project.githubUrl ? (
            <a
              href={project.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-muted-gray transition-colors hover:text-white"
            >
              GitHub
              <Github size={13} />
            </a>
          ) : null}
          {project.liveUrl ? (
            <a
              href={project.liveUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-muted-gray transition-colors hover:text-white"
            >
              Live demo ↗
            </a>
          ) : null}
        </div>
      </div>
    </motion.article>
  );
};
