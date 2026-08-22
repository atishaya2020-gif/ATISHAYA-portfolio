import { type Profile } from "../types/profile";

// TEMPORARY local content. Replace with Django REST API responses later.
export const profile: Profile = {
  name: "Atishaya Jain",
  role: "Backend-Focused Developer",
  introduction:
    "I'm a backend-focused developer particularly interested in backend systems and APIs, while staying capable of building full-stack applications.",
  philosophy:
    "I like building things from the ground up — turning ideas into working systems and learning through the process.",
  education: [
    {
      id: "education-1",
      label: "B.Tech CSE",
      title:
        "Specialisation in IoT with Cybersecurity including Blockchain",
      description:
        "CGC Landran · 2nd year · 3rd semester",
    },
  ],
  journey: [
    {
      id: "journey-1",
      label: "Now",
      title: "Learning Django REST Framework",
      description:
        "Currently learning Django REST Framework and API development — the same stack behind my deployed projects.",
    },
    {
      id: "journey-2",
      label: "Direction",
      title: "Backend systems first",
      description:
        "My projects move from Django fundamentals toward REST APIs: authentication, database models, and production deployments.",
    },
  ],
  currently: [
    { label: "Focus", value: "Backend systems" },
    { label: "Learning", value: "Django REST Framework" },
    { label: "Semester", value: "2nd year · 3rd sem" },
  ],
  currentFocus: [
    "Django REST Framework and API development",
    "Authentication, database models, and REST API design",
    "React frontends backed by real Django APIs",
  ],
  whatIBuild: [
    "Django applications with authentication, CRUD, and search",
    "REST APIs consumed by React frontends",
    "Production-deployed projects using PostgreSQL and Cloudinary",
  ],
  goals: [
    "Build real software and work on meaningful systems",
    "Keep learning as the work evolves",
    "Have opportunities to work in different places and environments",
  ],
};
