import { type ReactNode } from "react";
import { Footer } from "./Footer";

interface PageShellProps {
  children: ReactNode;
}

export const PageShell = ({ children }: PageShellProps) => {
  return (
    <div className="flex min-h-screen flex-col pt-28">
      <div className="mx-auto w-full max-w-6xl flex-1 px-6 pb-16">{children}</div>
      <Footer />
    </div>
  );
};
