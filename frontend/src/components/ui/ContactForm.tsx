import { useState, type ChangeEvent, type FormEvent } from "react";
import axios from "axios";
import { submitContactForm, type ContactSubmissionPayload } from "../../services/api";

interface FormState {
  name: string;
  email: string;
  subject: string;
  message: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  subject?: string;
  message?: string;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const ContactForm = () => {
  const [formData, setFormData] = useState<FormState>({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    const trimmedName = formData.name.trim();
    if (!trimmedName) {
      newErrors.name = "Name is required.";
    } else if (trimmedName.length > 150) {
      newErrors.name = "Name must be 150 characters or fewer.";
    }

    const trimmedEmail = formData.email.trim();
    if (!trimmedEmail) {
      newErrors.email = "Email is required.";
    } else if (!EMAIL_REGEX.test(trimmedEmail)) {
      newErrors.email = "Please enter a valid email address.";
    } else if (trimmedEmail.length > 254) {
      newErrors.email = "Email must be 254 characters or fewer.";
    }

    const trimmedSubject = formData.subject.trim();
    if (trimmedSubject.length > 200) {
      newErrors.subject = "Subject must be 200 characters or fewer.";
    }

    const trimmedMessage = formData.message.trim();
    if (!trimmedMessage) {
      newErrors.message = "Message is required.";
    } else if (trimmedMessage.length > 5000) {
      newErrors.message = "Message must be 5000 characters or fewer.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
    if (serverError) {
      setServerError(null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccessMessage(null);
    setServerError(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    const payload: ContactSubmissionPayload = {
      name: formData.name.trim(),
      email: formData.email.trim(),
      message: formData.message.trim(),
    };

    const trimmedSubject = formData.subject.trim();
    if (trimmedSubject) {
      payload.subject = trimmedSubject;
    }

    try {
      const response = await submitContactForm(payload);
      setSuccessMessage(response.message || "Your message has been received.");
      setFormData({ name: "", email: "", subject: "", message: "" });
      setErrors({});
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 429) {
          setServerError("You have submitted too many messages. Please try again later.");
        } else if (err.response?.status === 400 && err.response.data) {
          const apiErrors = err.response.data as Record<string, string[] | string>;
          const newErrors: FormErrors = {};
          let generalMsg = "Please check the form for errors.";

          if (typeof apiErrors === "object" && apiErrors !== null) {
            if (typeof apiErrors.detail === "string") {
              generalMsg = apiErrors.detail;
            }
            if (apiErrors.name) {
              newErrors.name = Array.isArray(apiErrors.name) ? apiErrors.name[0] : String(apiErrors.name);
            }
            if (apiErrors.email) {
              newErrors.email = Array.isArray(apiErrors.email) ? apiErrors.email[0] : String(apiErrors.email);
            }
            if (apiErrors.subject) {
              newErrors.subject = Array.isArray(apiErrors.subject) ? apiErrors.subject[0] : String(apiErrors.subject);
            }
            if (apiErrors.message) {
              newErrors.message = Array.isArray(apiErrors.message) ? apiErrors.message[0] : String(apiErrors.message);
            }
          }
          setErrors(newErrors);
          setServerError(generalMsg);
        } else {
          setServerError("Unable to send message right now. Please try again later or reach out directly by email.");
        }
      } else {
        setServerError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {successMessage && (
        <div
          role="status"
          aria-live="polite"
          className="border border-green-500/30 bg-green-500/10 p-5 text-sm text-green-400"
        >
          {successMessage}
        </div>
      )}

      {serverError && (
        <div
          role="alert"
          className="border border-raging-red/30 bg-raging-red/10 p-5 text-sm text-raging-red"
        >
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate aria-busy={isSubmitting}>
        <div>
          <label
            htmlFor="name"
            className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray"
          >
            Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            maxLength={150}
            value={formData.name}
            onChange={handleChange}
            disabled={isSubmitting}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? "name-error" : undefined}
            className="w-full border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red disabled:cursor-not-allowed disabled:opacity-50"
          />
          {errors.name && (
            <p id="name-error" className="mt-1 text-xs text-raging-red" role="alert">
              {errors.name}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray"
          >
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            maxLength={254}
            value={formData.email}
            onChange={handleChange}
            disabled={isSubmitting}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "email-error" : undefined}
            className="w-full border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red disabled:cursor-not-allowed disabled:opacity-50"
          />
          {errors.email && (
            <p id="email-error" className="mt-1 text-xs text-raging-red" role="alert">
              {errors.email}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="subject"
            className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray"
          >
            Subject <span className="text-[10px] lowercase text-muted-gray/70">(optional)</span>
          </label>
          <input
            id="subject"
            name="subject"
            type="text"
            maxLength={200}
            value={formData.subject}
            onChange={handleChange}
            disabled={isSubmitting}
            aria-invalid={!!errors.subject}
            aria-describedby={errors.subject ? "subject-error" : undefined}
            className="w-full border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red disabled:cursor-not-allowed disabled:opacity-50"
          />
          {errors.subject && (
            <p id="subject-error" className="mt-1 text-xs text-raging-red" role="alert">
              {errors.subject}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="message"
            className="mb-2 block text-[11px] font-bold uppercase tracking-[0.16em] text-muted-gray"
          >
            Message
          </label>
          <textarea
            id="message"
            name="message"
            rows={5}
            required
            maxLength={5000}
            value={formData.message}
            onChange={handleChange}
            disabled={isSubmitting}
            aria-invalid={!!errors.message}
            aria-describedby={errors.message ? "message-error" : undefined}
            className="w-full resize-y border border-white/10 bg-transparent px-4 py-3 text-sm outline-none transition-colors focus:border-raging-red disabled:cursor-not-allowed disabled:opacity-50"
          />
          {errors.message && (
            <p id="message-error" className="mt-1 text-xs text-raging-red" role="alert">
              {errors.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-raging-red px-5 py-3 text-xs font-bold uppercase tracking-[0.16em] transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Sending..." : "Send message"}
        </button>
      </form>
    </div>
  );
};
