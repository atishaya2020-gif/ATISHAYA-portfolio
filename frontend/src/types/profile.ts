export interface TimelineItem {
  id: string;
  label: string;
  title: string;
  description: string;
}

export interface StatusItem {
  label: string;
  value: string;
}

export interface Profile {
  name: string;
  role: string;
  introduction: string;
  philosophy?: string;
  education: TimelineItem[];
  journey: TimelineItem[];
  currently?: StatusItem[];
  currentFocus: string[];
  whatIBuild: string[];
  goals: string[];
}
