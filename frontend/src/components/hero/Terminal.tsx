import { motion } from "framer-motion";
import { usePrefersReducedMotion } from "../../hooks/useReducedMotion";

export const Terminal = () => {
  const reducedMotion = usePrefersReducedMotion();

  return (
    <div className="relative w-full max-w-md">
      <div className="pointer-events-none absolute -inset-8 bg-raging-red/8 blur-3xl" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:22px_22px] opacity-40" />

      <div className="relative overflow-hidden border border-white/10 bg-[#0c0c0c]">
        <div className="flex items-center justify-between border-b border-white/5 bg-white/[0.03] px-4 py-2.5">
          <div className="flex gap-1.5">
            <span className="h-2 w-2 rounded-full bg-white/15" />
            <span className="h-2 w-2 rounded-full bg-white/15" />
            <span className="h-2 w-2 rounded-full bg-white/15" />
          </div>
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-gray">
            atishaya@dev
          </span>
          <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-green-400">
            <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
            Online
          </span>
        </div>

        <div className="space-y-3 p-5 font-mono text-xs leading-relaxed">
          <div className="flex gap-2">
            <span className="text-raging-red">$</span>
            <span>whoami</span>
          </div>
          <div className="text-white/80">atishaya@developer</div>

          <div className="space-y-1 pt-2">
            {["building", "learning", "shipping"].map((line, index) => (
              <motion.div
                key={line}
                initial={reducedMotion ? false : { opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: reducedMotion ? 0 : 0.7 + index * 0.25 }}
                className="flex gap-2 text-white"
              >
                <span className="text-raging-red">{">"}</span>
                <span>{line}</span>
              </motion.div>
            ))}
          </div>

          <div className="flex items-center justify-between border-t border-white/5 pt-4 text-[10px] uppercase tracking-[0.16em] text-muted-gray">
            <span>status: online</span>
            <span>python • django • react</span>
          </div>
        </div>
      </div>
    </div>
  );
};
