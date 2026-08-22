import { Github, Linkedin, Mail } from "lucide-react";
import { Link } from "react-router-dom";
import { Section } from "../layout/Section";
import { SITE } from "../../lib/site";

export const Contact = () => {
  return (
    <Section id="contact" title="CONTACT">
      <div className="max-w-3xl">
        <h2 className="mb-5 text-4xl font-black uppercase leading-[0.9] tracking-tighter md:text-6xl">
          LET'S BUILD
          <br />
          <span className="text-raging-red">SOMETHING.</span>
        </h2>
        <p className="mb-8 max-w-xl text-base leading-relaxed text-muted-gray">
          Open to new opportunities and collaborations. If you have a project in
          mind, reach out.
        </p>
        <div className="mb-8 flex flex-wrap gap-5">
          {SITE.email ? (
            <a
              href={`mailto:${SITE.email}`}
              className="group flex items-center gap-3 transition-colors hover:text-raging-red"
            >
              <div className="border border-white/10 bg-white/5 p-3 transition-colors group-hover:border-raging-red/40">
                <Mail size={16} />
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-muted-gray">
                  Email
                </div>
                <div className="text-sm font-bold">{SITE.email}</div>
              </div>
            </a>
          ) : null}
          {SITE.github ? (
            <a
              href={SITE.github}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-3 transition-colors hover:text-raging-red"
            >
              <div className="border border-white/10 bg-white/5 p-3 transition-colors group-hover:border-raging-red/40">
                <Github size={16} />
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-muted-gray">
                  GitHub
                </div>
                <div className="text-sm font-bold">GitHub</div>
              </div>
            </a>
          ) : null}
          {SITE.linkedin ? (
            <a
              href={SITE.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-3 transition-colors hover:text-raging-red"
            >
              <div className="border border-white/10 bg-white/5 p-3 transition-colors group-hover:border-raging-red/40">
                <Linkedin size={16} />
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-muted-gray">
                  LinkedIn
                </div>
                <div className="text-sm font-bold">LinkedIn</div>
              </div>
            </a>
          ) : null}
        </div>
        <Link
          to="/contact"
          className="inline-flex border border-white/10 px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:border-raging-red"
        >
          Open contact
        </Link>
      </div>
    </Section>
  );
};
