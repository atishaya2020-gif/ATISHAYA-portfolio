import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export interface ApiTechnology {
  id: number;
  name: string;
  category: string;
  slug: string;
  description: string;
  order: number;
}

export interface ApiProjectFeature {
  id: number;
  text: string;
  order: number;
}

export interface ApiProjectArchitecture {
  id: number;
  text: string;
  order: number;
}

export interface ApiProject {
  id: number;
  title: string;
  subtitle: string;
  slug: string;
  short_description: string;
  full_description: string;
  category: string;
  status: string;
  featured: boolean;
  order: number;
  github_url: string;
  live_url: string;
  api_url: string;
  overview: string;
  technologies: ApiTechnology[];
  features: ApiProjectFeature[];
  architecture: ApiProjectArchitecture[];
  created_at: string;
  updated_at: string;
}

export interface ApiEducation {
  id: number;
  label: string;
  title: string;
  description: string;
  order: number;
}

export interface ApiProfileFocus {
  id: number;
  label: string;
  value: string;
  order: number;
}

export interface ApiProfile {
  id: number;
  name: string;
  role: string;
  introduction: string;
  philosophy: string;
  career_goal: string;
  current_focus: string;
  what_i_build: string;
  education: ApiEducation[];
  focus_items: ApiProfileFocus[];
}

export async function fetchProjects(): Promise<ApiProject[]> {
  const { data } = await apiClient.get<ApiProject[]>("/projects/");
  return data;
}

export async function fetchProjectBySlug(
  slug: string,
): Promise<ApiProject | null> {
  try {
    const { data } = await apiClient.get<ApiProject>(`/projects/${slug}/`);
    return data;
  } catch (error: unknown) {
    if (
      axios.isAxiosError(error) &&
      (error.response?.status === 404 || error.response?.status === 400)
    ) {
      return null;
    }
    throw error;
  }
}

export async function fetchTechnologies(): Promise<ApiTechnology[]> {
  const { data } = await apiClient.get<ApiTechnology[]>("/technologies/");
  return data;
}

export async function fetchProfile(): Promise<ApiProfile | null> {
  try {
    const { data } = await apiClient.get<ApiProfile>("/profile/");
    return data;
  } catch (error: unknown) {
    if (
      axios.isAxiosError(error) &&
      (error.response?.status === 404 || error.response?.status === 400)
    ) {
      return null;
    }
    throw error;
  }
}

export interface ContactSubmissionPayload {
  name: string;
  email: string;
  subject?: string;
  message: string;
}

export interface ContactSubmissionResponse {
  status: string;
  message: string;
}

export async function submitContactForm(
  payload: ContactSubmissionPayload,
): Promise<ContactSubmissionResponse> {
  const { data } = await apiClient.post<ContactSubmissionResponse>(
    "/contact/",
    payload,
  );
  return data;
}
