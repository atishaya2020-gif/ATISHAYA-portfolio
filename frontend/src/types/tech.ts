export type TechCategory =
  | "frontend"
  | "backend"
  | "database"
  | "tools"
  | "languages"
  | "apis"
  | "deployment";

export interface Technology {
  id: string;
  name: string;
  category: TechCategory;
  description: string;
  icon?: string;
  relatedProjects?: string[];
}
