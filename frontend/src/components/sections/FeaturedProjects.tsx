import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Section } from "../layout/Section";
import { ProjectCard } from "../projects/ProjectCard";
import { getFeaturedProjects } from "../../services/content";
import { type Project } from "../../types/project";

export const FeaturedProjects = () => {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    void getFeaturedProjects().then(setProjects);
  }, []);

  return (
    <Section id="projects" title="PROJECTS">
      <div className="mb-6 flex items-end justify-between gap-4">
        <p className="max-w-xl text-sm text-muted-gray">
          Featured work. Case studies expand on the architecture, constraints, and
          what comes next.
        </p>
        <Link
          to="/projects"
          className="shrink-0 text-[11px] font-bold uppercase tracking-[0.16em] text-raging-red"
        >
          All projects →
        </Link>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </Section>
  );
};
