import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Terminal } from "./Terminal";
import { usePrefersReducedMotion } from "../../hooks/useReducedMotion";
import { SITE } from "../../lib/site";

export const Hero = () => {
  const reducedMotion = usePrefersReducedMotion();

  return (
    <section className="relative flex min-h-[88vh] items-center overflow-hidden pt-24 pb-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(225,29,46,0.08),transparent_32%),radial-gradient(circle_at_80%_30%,rgba(225,29,46,0.05),transparent_28%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative mx-auto grid w-full max-w-6xl items-center gap-12 px-6 lg:grid-cols-[1.1fr_0.9fr]">
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <p className="mb-5 font-mono text-[11px] uppercase tracking-[0.28em] text-raging-red">
            {SITE.role}
          </p>
          <h1 className="mb-7 text-5xl font-black leading-[0.88] tracking-tighter sm:text-6xl lg:text-7xl">
            FROM IDEAS
            <br />
            TO <span className="text-raging-red">WORKING</span>
            <br />
            SYSTEMS.
          </h1>

          <p className="mb-5 font-mono text-sm text-muted-gray sm:text-base">
            Python <span className="text-raging-red">•</span> Django{" "}
            <span className="text-raging-red">•</span> REST APIs{" "}
            <span className="text-raging-red">•</span> React
          </p>

          <p className="mb-8 max-w-lg text-base leading-relaxed text-muted-gray">
            I like building things from the ground up — turning ideas into
            working systems and learning through the process.
          </p>

          <div className="flex flex-wrap gap-3">
            <Link
              to="/projects"
              className="group inline-flex items-center gap-2 bg-raging-red px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:bg-red-700"
            >
              Explore my work
              <ArrowRight
                size={15}
                className="transition-transform group-hover:translate-x-1"
              />
            </Link>
            {SITE.github ? (
              <a
                href={SITE.github}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 border border-white/10 px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:border-raging-red hover:bg-white/5"
              >
                GitHub ↗
              </a>
            ) : (
              <span className="inline-flex items-center gap-2 border border-white/10 px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] text-muted-gray">
                GitHub ↗
              </span>
            )}
          </div>
        </motion.div>

        <motion.div
          className="flex justify-center lg:justify-end"
          initial={reducedMotion ? false : { opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: reducedMotion ? 0 : 0.2, duration: 0.7 }}
        >
          <Terminal />
        </motion.div>
      </div>
    </section>
  );
};
