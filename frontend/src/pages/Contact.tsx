import { Github, Linkedin, Mail } from "lucide-react";
import { motion } from "framer-motion";
import { PageShell } from "../components/layout/PageShell";
import { PageHeader } from "../components/ui/PageHeader";
import { ContactForm } from "../components/ui/ContactForm";
import { SITE } from "../lib/site";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { usePrefersReducedMotion } from "../hooks/useReducedMotion";

export const Contact = () => {
  const reducedMotion = usePrefersReducedMotion();
  useDocumentMeta({
    title: "Contact",
    description: "Contact Atishaya Jain about collaborations and projects.",
  });

  return (
    <PageShell>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          kicker="Contact"
          title="Let's build something."
          description="Open to opportunities, collaborations, and questions about my work. Email reaches me fastest — or use the form."
        />

        <div className="grid gap-12 md:grid-cols-2">
          <div className="space-y-5">
            {SITE.email ? (
              <a
                href={`mailto:${SITE.email}`}
                className="group flex items-center gap-3 transition-colors hover:text-raging-red"
              >
                <div className="border border-white/10 bg-white/5 p-3">
                  <Mail size={16} />
                </div>
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-widest text-muted-gray">
                    Email
                  </div>
                  <div className="text-sm font-bold">{SITE.email}</div>
                </div>
              </a>
            ) : (
              <p className="text-sm text-muted-gray">Email not configured yet.</p>
            )}
            {SITE.github ? (
              <a
                href={SITE.github}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-3 transition-colors hover:text-raging-red"
              >
                <div className="border border-white/10 bg-white/5 p-3">
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
                <div className="border border-white/10 bg-white/5 p-3">
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
          <ContactForm />
        </div>
      </motion.div>
    </PageShell>
  );
};
