interface ProjectVisualProps {
  title: string;
  className?: string;
}

export const ProjectVisual = ({ title, className = "" }: ProjectVisualProps) => {
  return (
    <div
      className={`relative overflow-hidden bg-[#0b0b0b] ${className}`}
      aria-hidden="true"
    >
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:28px_28px]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_30%,rgba(225,29,46,0.18),transparent_42%)]" />
      <div className="absolute inset-0 flex flex-col justify-between p-5">
        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-white/35">
          Project preview
        </span>
        <span className="max-w-[80%] text-sm font-bold uppercase tracking-[0.12em] text-white/50">
          {title}
        </span>
      </div>
    </div>
  );
};
