import { useEffect } from "react";
import { SITE } from "../lib/site";

interface DocumentMeta {
  title?: string;
  description?: string;
}

export const useDocumentMeta = ({ title, description }: DocumentMeta) => {
  useEffect(() => {
    const previousTitle = document.title;
    const previousDescription = document
      .querySelector('meta[name="description"]')
      ?.getAttribute("content");

    document.title = title
      ? `${title} — ${SITE.displayName}`
      : `${SITE.displayName} — ${SITE.role}`;

    let descriptionTag = document.querySelector('meta[name="description"]');
    if (!descriptionTag) {
      descriptionTag = document.createElement("meta");
      descriptionTag.setAttribute("name", "description");
      document.head.appendChild(descriptionTag);
    }
    descriptionTag.setAttribute("content", description ?? SITE.description);

    return () => {
      document.title = previousTitle;
      if (previousDescription) {
        descriptionTag.setAttribute("content", previousDescription);
      }
    };
  }, [title, description]);
};
