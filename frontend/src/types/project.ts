export type ProjectStatus = "in-progress" | "completed" | "archived";

export type ProjectCategory =
  | "fullstack"
  | "frontend"
  | "backend"
  | "tooling";

export interface Project {
  id: string;
  slug: string;
  order: number;
  title: string;
  subtitle?: string;
  shortDescription: string;
  fullDescription?: string;
  category: ProjectCategory;
  status: ProjectStatus;
  featured: boolean;
  technologies: string[];
  image?: string;
  githubUrl?: string;
  liveUrl?: string;
  apiUrl?: string;
  architecture?: string[];
  year?: string;
  role?: string;
  overview?: string;
  features?: string[];
  challenges?: string[];
  outcomes?: string[];
}
