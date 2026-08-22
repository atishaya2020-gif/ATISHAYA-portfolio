interface PageHeaderProps {
  kicker: string;
  title: string;
  description?: string;
}

export const PageHeader = ({ kicker, title, description }: PageHeaderProps) => {
  return (
    <header className="mb-12">
      <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.22em] text-raging-red">
        {kicker}
      </p>
      <h1 className="mb-4 text-4xl font-black uppercase tracking-tighter md:text-6xl">
        {title}
      </h1>
      {description ? (
        <p className="max-w-2xl text-base leading-relaxed text-muted-gray">
          {description}
        </p>
      ) : null}
    </header>
  );
};
