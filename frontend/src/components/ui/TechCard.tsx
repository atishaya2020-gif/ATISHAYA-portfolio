import { type Technology } from "../../types/tech";

interface TechCardProps {
  tech: Technology;
}

export const TechCard = ({ tech }: TechCardProps) => {
  return (
    <article className="group border border-white/5 bg-white/[0.02] p-4 transition-all duration-300 hover:border-raging-red/40 hover:bg-white/[0.04]">
      <div className="mb-3 flex items-start justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-raging-red">
          {tech.category}
        </span>
        <span className="h-1.5 w-1.5 rounded-full bg-white/20 transition-colors group-hover:bg-raging-red" />
      </div>
      <h3 className="mb-1 font-bold tracking-tight text-white transition-colors group-hover:text-raging-red">
        {tech.name}
      </h3>
      <p className="font-mono text-xs text-muted-gray">{tech.description}</p>
    </article>
  );
};
