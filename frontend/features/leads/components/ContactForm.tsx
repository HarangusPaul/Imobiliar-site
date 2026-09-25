"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import {
  Checkbox,
  CheckIcon,
  Field,
  FormAlert,
  GoldButton,
  PhoneInput,
  Select,
  splitE164,
  TextInput,
  toE164,
} from "@/components/ui/form/controls";
import {
  ChipGroup,
  fieldWidth,
  FormBlock,
  OptionCards,
  TextArea,
  type OptionCard,
} from "@/components/ui/form/sections";
import { routes } from "@/lib/constants/routes";
import { emptyFormState, firstError, formStateFromError, type FormState } from "@/lib/validation/form";
import type { Account } from "@/types/account";

import { submitLead } from "../api";
import { leadSchema } from "../schema";
import type { LeadKind, LeadReceipt } from "../types";

import styles from "./ContactForm.module.css";

/**
 * The general contact form. Posts a lead; the topic becomes the lead kind
 * where one fits and is written into the message either way, so the advisor
 * sees it in the inbox.
 */

const MESSAGE_MAX = 1000;

type Topic = "buying" | "renting" | "stays" | "listing" | "press" | "other";

const TOPICS: Array<{ value: Topic; label: string; kind: LeadKind }> = [
  { value: "buying", label: "Buying", kind: "general" },
  { value: "renting", label: "Renting", kind: "general" },
  { value: "stays", label: "Hotel stays", kind: "general" },
  { value: "listing", label: "Listing my property", kind: "valuation" },
  { value: "press", label: "Press", kind: "general" },
  { value: "other", label: "Something else", kind: "general" },
];

type Preference = "phone" | "sms" | "email";

const PREFERENCES: OptionCard<Preference>[] = [
  {
    value: "phone",
    title: "Phone call",
    description: "We call at a time that suits you",
    icon: <path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 5 5L14 12l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z" />,
  },
  {
    value: "sms",
    title: "Text message",
    description: "A quick reply by SMS",
    icon: (
      <>
        <path d="M4 5h16v11H9l-5 4z" />
        <path d="M8 10h8M8 13h5" />
      </>
    ),
  },
  {
    value: "email",
    title: "Email",
    description: "A detailed written reply",
    icon: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2.5" />
        <path d="M4 7l8 6 8-6" />
      </>
    ),
  },
];

export interface ListingOption {
  value: string;
  label: string;
}

interface ContactFormProps {
  account: Account | null;
  /** Curated listings for "Property you are interested in". */
  listings: ListingOption[];
  initialTopic?: string;
  initialListing?: string;
}

export function ContactForm({ account, listings, initialTopic, initialListing }: ContactFormProps) {
  const phone = account ? splitE164(account.phone_number) : { country: "RO", number: "" };

  const [topic, setTopic] = useState<Topic>(
    TOPICS.find((t) => t.value === initialTopic)?.value ?? "buying",
  );
  const [fullName, setFullName] = useState(
    account ? [account.first_name, account.last_name].filter(Boolean).join(" ") : "",
  );
  const [country, setCountry] = useState(phone.country);
  const [number, setNumber] = useState(phone.number);
  const [email, setEmail] = useState(account?.email ?? "");
  const [listing, setListing] = useState(
    listings.some((l) => l.value === initialListing) ? initialListing! : "",
  );
  const [preference, setPreference] = useState<Preference>("phone");
  const [message, setMessage] = useState("");
  const [consent, setConsent] = useState(false);
  const [website, setWebsite] = useState("");
  const [state, setState] = useState<FormState>(emptyFormState);
  const [pending, setPending] = useState(false);
  const [receipt, setReceipt] = useState<LeadReceipt | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const topicDef = TOPICS.find((t) => t.value === topic)!;
    const listingLabel = listings.find((l) => l.value === listing)?.label;

    const values = {
      full_name: fullName,
      phone_number: number ? toE164(country, number) : "",
      email: email.trim(),
      message: message.trim(),
      contact_preference: preference,
      source_path: routes.contact,
      website,
    };
    const parsed = leadSchema.safeParse(values);
    const fieldErrors: Record<string, string[]> = parsed.success
      ? {}
      : { ...parsed.error.flatten().fieldErrors };
    if (preference === "email" && !values.email) {
      fieldErrors.email = ["Add an email so we can reply by email."];
    }
    if (!consent) fieldErrors.consent = ["Please agree so we can reply to you."];
    if (!parsed.success || Object.keys(fieldErrors).length) {
      setState({ fieldErrors, formError: "" });
      return;
    }

    const header = [`Topic: ${topicDef.label}`, listingLabel ? `Interested in: ${listingLabel}` : ""]
      .filter(Boolean)
      .join("\n");

    setPending(true);
    setState(emptyFormState);
    try {
      const result = await submitLead({
        ...parsed.data,
        email: parsed.data.email || undefined,
        kind: topicDef.kind,
        message: `${header}\n\n${values.message}`.slice(0, 4000),
      });
      setReceipt(result);
    } catch (error) {
      setState(formStateFromError(error));
    } finally {
      setPending(false);
    }
  };

  if (receipt) {
    return (
      <div className={styles.success} role="status">
        <span className={styles.successIcon} aria-hidden="true">
          <CheckIcon size={22} />
        </span>
        <h2 className={styles.successTitle}>Message sent</h2>
        <p className={styles.successText}>
          Thank you, {fullName.split(" ")[0]}. An advisor will reply by{" "}
          {PREFERENCES.find((p) => p.value === preference)!.title.toLowerCase()} within one working day.
        </p>
        <p className={styles.successRef}>Reference {receipt.id.slice(0, 8).toUpperCase()}</p>
        <div className={styles.successActions}>
          <GoldButton href={routes.buy}>Browse the collection</GoldButton>
          <Link href={routes.home} className={styles.textLink}>
            Back to home
          </Link>
        </div>
      </div>
    );
  }

  const invalid = (field: string) => Boolean(firstError(state, field));

  return (
    <form onSubmit={onSubmit} noValidate>
      <FormBlock
        id="message"
        marker={
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="5" width="18" height="14" rx="2.5" />
            <path d="M4 7l8 6 8-6" />
          </svg>
        }
        title="Send us a message"
        description="Tell us what you are looking for. An advisor will reply within one working day."
        footer={
          <div className={styles.sendRow}>
            <Field
              label={<span className="visually-hidden">Consent</span>}
              error={firstError(state, "consent")}
              className={styles.consent}
            >
              <Checkbox checked={consent} onChange={setConsent} invalid={invalid("consent")}>
                <span className={styles.consentText}>
                  I agree that Monument may contact me about my enquiry. Read our{" "}
                  <Link href={routes.about}>Privacy policy</Link>.
                </span>
              </Checkbox>
            </Field>
            <GoldButton loading={pending}>Send message</GoldButton>
          </div>
        }
      >
        <Field label="What is it about?" asGroup className={fieldWidth.full}>
          <ChipGroup
            name="topic"
            options={TOPICS}
            selected={[topic]}
            onToggle={(v) => setTopic(v as Topic)}
          />
        </Field>

        <Field label="Full name" htmlFor="c-name" className={fieldWidth.half} error={firstError(state, "full_name")}>
          <TextInput
            id="c-name"
            autoComplete="name"
            placeholder="Your name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            invalid={invalid("full_name")}
          />
        </Field>

        <Field label="Phone number" htmlFor="c-phone" className={fieldWidth.half} error={firstError(state, "phone_number")}>
          <PhoneInput
            id="c-phone"
            country={country}
            onCountryChange={setCountry}
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            placeholder="721 234 567"
            invalid={invalid("phone_number")}
          />
        </Field>

        <Field
          label="Email"
          optional={preference !== "email"}
          htmlFor="c-email"
          className={fieldWidth.half}
          error={firstError(state, "email")}
        >
          <TextInput
            id="c-email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            invalid={invalid("email")}
          />
        </Field>

        <Field label="Property you are interested in" optional htmlFor="c-listing" className={fieldWidth.half}>
          <Select
            id="c-listing"
            value={listing}
            onChange={(e) => setListing(e.target.value)}
            placeholder="Choose a listing"
            options={listings}
          />
        </Field>

        <Field label="How should we reach you?" asGroup className={fieldWidth.full}>
          <OptionCards name="preference" value={preference} options={PREFERENCES} onChange={setPreference} />
        </Field>

        <Field label="Your message" htmlFor="c-message" className={fieldWidth.full} error={firstError(state, "message")}>
          <TextArea
            id="c-message"
            value={message}
            onChange={setMessage}
            max={MESSAGE_MAX}
            placeholder="Where, what size, which dates, what matters most to you…"
            invalid={invalid("message")}
          />
        </Field>

        {/* Honeypot: people never see or fill this; bots do. */}
        <input
          type="text"
          name="website"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          className={styles.honeypot}
        />

        {state.formError ? (
          <div className={fieldWidth.full}>
            <FormAlert>{state.formError}</FormAlert>
          </div>
        ) : null}
      </FormBlock>
    </form>
  );
}
