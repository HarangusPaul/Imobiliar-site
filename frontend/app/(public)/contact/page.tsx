import type { Metadata } from "next";

/**
 * `/contact` - the general contact form.
 *
 * The form is a client component from `features/leads`; this page is a server
 * component that renders it. Submission posts to the public lead endpoint,
 * which is rate-limited and honeypot-protected server-side.
 */

export const metadata: Metadata = {
  title: "Contact",
  description: "Get in touch with our team.",
};

export default function ContactPage() {
  return (
    <div>
      <h1>Contact us</h1>
      {/* <ContactForm /> from features/leads */}
    </div>
  );
}
