import { useReducedMotion as useFramerReducedMotion } from "framer-motion";

export const usePrefersReducedMotion = () => {
  return useFramerReducedMotion() ?? false;
};
