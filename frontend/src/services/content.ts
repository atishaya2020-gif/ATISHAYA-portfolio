import { projects } from "../data/projects";
import { technologies } from "../data/tech";
import { profile } from "../data/profile";
import { type Project } from "../types/project";
import { type Technology, type TechCategory } from "../types/tech";
import { type Profile } from "../types/profile";
import {
  fetchProjects,
  fetchProjectBySlug,
  fetchTechnologies,
  fetchProfile,
} from "./api";
import { mapApiProject, mapApiProfile, mapApiTechnology } from "./mappers";

const cache = new Map<string, Promise<unknown>>();

function cacheKey(prefix: string, ...args: string[]): string {
  return args.length ? `${prefix}:${args.join(":")}` : prefix;
}

function fetchWithCache<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const existing = cache.get(key) as Promise<T> | undefined;
  if (existing) return existing;
  const promise = fetcher();
  cache.set(key, promise);
  return promise;
}

export async function getProjects(): Promise<Project[]> {
  try {
    return await fetchWithCache("projects", async () => {
      const data = await fetchProjects();
      return data.map(mapApiProject);
    });
  } catch (err) {
    if (import.meta.env.DEV) {
      console.debug("[portfolio] API unavailable, using static projects", err);
    }
    return projects;
  }
}

export async function getFeaturedProjects(): Promise<Project[]> {
  try {
    return await fetchWithCache("featured", async () => {
      const data = await fetchProjects();
      return data
        .filter((p) => p.featured)
        .map(mapApiProject)
        .sort((a, b) => a.order - b.order);
    });
  } catch (err) {
    if (import.meta.env.DEV) {
      console.debug(
        "[portfolio] API unavailable, using static featured projects",
        err,
      );
    }
    return projects.filter((p) => p.featured).sort((a, b) => a.order - b.order);
  }
}

export async function getProjectBySlug(
  slug: string,
): Promise<Project | null> {
  try {
    return await fetchWithCache(cacheKey("project", slug), async () => {
      const data = await fetchProjectBySlug(slug);
      return data ? mapApiProject(data) : null;
    });
  } catch (err) {
    if (import.meta.env.DEV) {
      console.debug(
        "[portfolio] API unavailable, using static project for",
        slug,
        err,
      );
    }
    return projects.find((p) => p.slug === slug) ?? null;
  }
}

export async function getTechnologies(): Promise<Technology[]> {
  try {
    return await fetchWithCache("technologies", async () => {
      const data = await fetchTechnologies();
      return data.map(mapApiTechnology);
    });
  } catch (err) {
    if (import.meta.env.DEV) {
      console.debug(
        "[portfolio] API unavailable, using static technologies",
        err,
      );
    }
    return technologies;
  }
}

export async function getTechnologiesByCategory(
  category: TechCategory,
): Promise<Technology[]> {
  const all = await getTechnologies();
  return all.filter((tech) => tech.category === category);
}

export async function getProfile(): Promise<Profile> {
  try {
    return await fetchWithCache("profile", async () => {
      const data = await fetchProfile();
      return data ? mapApiProfile(data, profile) : profile;
    });
  } catch (err) {
    if (import.meta.env.DEV) {
      console.debug("[portfolio] API unavailable, using static profile", err);
    }
    return profile;
  }
}
