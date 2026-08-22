import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Section } from "../layout/Section";
import { getProfile } from "../../services/content";
import { type Profile } from "../../types/profile";

export const AboutPreview = () => {
  const [data, setData] = useState<Profile | null>(null);

  useEffect(() => {
    void getProfile().then(setData);
  }, []);

  if (!data) return null;

  return (
    <Section id="about" title="ABOUT">
      <div className="grid gap-8 md:grid-cols-3">
        <div className="space-y-4 text-base leading-relaxed text-muted-gray md:col-span-2">
          <p>{data.introduction}</p>
          <p>{data.currentFocus[0]}</p>
          <Link
            to="/about"
            className="inline-flex pt-2 text-xs font-bold uppercase tracking-[0.16em] text-raging-red"
          >
            Read more →
          </Link>
        </div>
        <div className="border border-white/5 bg-white/[0.03] p-5">
          <h3 className="mb-5 text-[11px] font-bold uppercase tracking-[0.2em] text-white">
            Currently
          </h3>
          <div className="space-y-5">
            {(data.currently ?? []).map((item) => (
              <div key={item.label}>
                <div className="mb-1 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-gray">
                  {item.label}
                </div>
                <div className="text-lg font-black uppercase leading-tight">
                  {item.value}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Section>
  );
};
