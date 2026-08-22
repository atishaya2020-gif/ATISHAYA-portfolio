import { type Project, type ProjectStatus } from "../types/project";
import { type Technology, type TechCategory } from "../types/tech";
import { type Profile } from "../types/profile";
import { projectImages } from "../data/projectImages";
import {
  type ApiProject,
  type ApiProfile,
  type ApiTechnology,
} from "./api";

const API_TECH_CATEGORY_MAP: Record<string, TechCategory> = {
  backend: "backend",
  frontend: "frontend",
  database: "database",
  cloud_deployment: "deployment",
  tools: "tools",
};

const API_STATUS_MAP: Record<string, ProjectStatus> = {
  in_progress: "in-progress",
  completed: "completed",
  archived: "archived",
};

export function mapApiTechnology(api: ApiTechnology): Technology {
  return {
    id: api.slug,
    name: api.name,
    category: API_TECH_CATEGORY_MAP[api.category] ?? api.category,
    description: api.description,
  };
}

export function mapApiProject(api: ApiProject): Project {
  return {
    id: api.slug,
    slug: api.slug,
    order: api.order,
    title: api.title,
    subtitle: api.subtitle || undefined,
    shortDescription: api.short_description,
    fullDescription: api.full_description || undefined,
    category: api.category as Project["category"],
    status: API_STATUS_MAP[api.status] ?? api.status,
    featured: api.featured,
    technologies: api.technologies.map((t) => t.name),
    image: projectImages[api.slug] ?? undefined,
    githubUrl: api.github_url || undefined,
    liveUrl: api.live_url || undefined,
    apiUrl: api.api_url || undefined,
    overview: api.overview || undefined,
    features: api.features.map((f) => f.text),
    architecture: api.architecture.map((a) => a.text),
  };
}

export function mapApiProfile(api: ApiProfile, staticProfile: Profile): Profile {
  const currentFocus = api.current_focus
    ? api.current_focus
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean)
    : staticProfile.currentFocus;

  const whatIBuild = api.what_i_build
    ? api.what_i_build
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean)
    : staticProfile.whatIBuild;

  const goals = api.career_goal ? [api.career_goal] : staticProfile.goals;

  return {
    ...staticProfile,
    name: api.name || staticProfile.name,
    role: api.role || staticProfile.role,
    introduction: api.introduction || staticProfile.introduction,
    philosophy: api.philosophy || staticProfile.philosophy,
    education: api.education.length
      ? api.education.map((e) => ({
          id: String(e.id),
          label: e.label,
          title: e.title,
          description: e.description,
        }))
      : staticProfile.education,
    currently: api.focus_items.length
      ? api.focus_items.map((f) => ({ label: f.label, value: f.value }))
      : staticProfile.currently,
    currentFocus,
    whatIBuild,
    goals,
  };
}
