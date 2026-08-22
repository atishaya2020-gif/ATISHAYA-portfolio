import { SITE } from "../../lib/site";

export const Footer = () => {
  return (
    <footer className="border-t border-white/5 py-8 text-center text-sm text-muted-gray">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-white">
          {SITE.name}
        </div>
        <p className="mb-4 text-xs opacity-60">Built with React.</p>
        <div className="flex justify-center gap-5 text-[10px] font-bold uppercase tracking-[0.18em]">
          {SITE.github ? (
            <a href={SITE.github} target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-raging-red">
              GitHub
            </a>
          ) : null}
          {SITE.linkedin ? (
            <a href={SITE.linkedin} target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-raging-red">
              LinkedIn
            </a>
          ) : null}
        </div>
      </div>
    </footer>
  );
};
