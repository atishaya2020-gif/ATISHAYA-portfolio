import { useState, type FormEvent } from "react";

export const ContactForm = () => {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <p className="border border-white/10 bg-white/[0.03] p-5 text-sm text-muted-gray">
        Thanks for the message. The form isn't wired to a backend yet — please reach me directly by email instead.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <div>
        <label htmlFor="name" className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray">
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          className="w-full border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red"
        />
      </div>
      <div>
        <label htmlFor="email" className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="w-full border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red"
        />
      </div>
      <div>
        <label htmlFor="message" className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          className="w-full resize-y border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red"
        />
      </div>
      <button
        type="submit"
        className="bg-raging-red px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:bg-red-700"
      >
        Send message
      </button>
    </form>
  );
};
