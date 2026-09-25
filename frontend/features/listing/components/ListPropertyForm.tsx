"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";

import {
  CheckIcon,
  Field,
  FormAlert,
  GoldButton,
  PhoneInput,
  Segmented,
  Select,
  splitE164,
  Stepper,
  TextInput,
  toE164,
  ToggleRow,
} from "@/components/ui/form/controls";
import { ChipGroup, fieldWidth, FormBlock, OptionCards, TextArea } from "@/components/ui/form/sections";
import { routes } from "@/lib/constants/routes";
import { formStateFromError } from "@/lib/validation/form";
import type { Account } from "@/types/account";

import { submitListing, type ListingReceipt } from "../api";
import {
  AMENITIES,
  CATEGORY_LABELS,
  composeMessage,
  COUNTRIES,
  CURRENCIES,
  DESCRIPTION_MAX,
  emptyDraft,
  groupDigits,
  LISTING_TYPES,
  pricingCopy,
  PROPERTY_TYPES,
  sectionErrors,
  SECTIONS,
  type ListingDraft,
  type ListingType,
  type SectionId,
} from "../model";

import styles from "./ListPropertyForm.module.css";
import { PhotoUpload, type Photo } from "./PhotoUpload";

/**
 * The owner questionnaire: eight sections with a sticky progress card.
 * Answers autosave to this browser (photos excepted) so an owner can leave
 * and come back; "Submit for review" sends everything to the advisors.
 */

const DRAFT_KEY = "monument:listing-draft:v1";

function readDraft(): { draft: ListingDraft; savedAt: number } | null {
  try {
    const raw = window.localStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { draft: Partial<ListingDraft>; savedAt: number };
    return { draft: { ...emptyDraft, ...parsed.draft }, savedAt: parsed.savedAt };
  } catch {
    return null;
  }
}

function writeDraft(draft: ListingDraft): number | null {
  try {
    const savedAt = Date.now();
    window.localStorage.setItem(DRAFT_KEY, JSON.stringify({ draft, savedAt }));
    return savedAt;
  } catch {
    return null;
  }
}

function clearDraft() {
  try {
    window.localStorage.removeItem(DRAFT_KEY);
  } catch {
    /* storage unavailable */
  }
}

function relativeTime(then: number, now: number): string {
  const minutes = Math.floor((now - then) / 60_000);
  if (minutes < 1) return "just now";
  if (minutes === 1) return "1 minute ago";
  if (minutes < 60) return `${minutes} minutes ago`;
  const hours = Math.floor(minutes / 60);
  return hours === 1 ? "1 hour ago" : `${hours} hours ago`;
}

// ---- Icons ------------------------------------------------------------------

const TYPE_ICONS: Record<ListingType, ReactNode> = {
  sell: <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" />,
  rent: (
    <>
      <rect x="3" y="4" width="18" height="17" rx="2" />
      <path d="M3 9h18M8 2v4M16 2v4" />
    </>
  ),
  stay: (
    <>
      <path d="M3 18V8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5" />
      <circle cx="7" cy="11" r="2" />
    </>
  ),
};

function PinIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z" />
      <circle cx="12" cy="9.5" r="2.5" />
    </svg>
  );
}

// ---- Form -------------------------------------------------------------------

export function ListPropertyForm({ account }: { account: Account }) {
  const router = useRouter();

  const prefill = useMemo<ListingDraft>(() => {
    const phone = splitE164(account.phone_number);
    return {
      ...emptyDraft,
      contactName: [account.first_name, account.last_name].filter(Boolean).join(" "),
      contactCountry: phone.country,
      contactPhone: phone.number,
    };
  }, [account]);

  const [draft, setDraft] = useState<ListingDraft>(prefill);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [showErrors, setShowErrors] = useState(false);
  const [current, setCurrent] = useState<SectionId>(SECTIONS[0]!.id);
  const [pending, setPending] = useState(false);
  const [formError, setFormError] = useState("");
  const [receipt, setReceipt] = useState<ListingReceipt | null>(null);

  // Restore a saved draft once, after hydration.
  useEffect(() => {
    const saved = readDraft();
    if (saved) {
      setDraft(saved.draft);
      setSavedAt(saved.savedAt);
    }
    setLoaded(true);
  }, []);

  // Autosave shortly after the owner stops typing.
  useEffect(() => {
    if (!loaded || receipt) return;
    const timer = window.setTimeout(() => {
      const at = writeDraft(draft);
      if (at) setSavedAt(at);
    }, 800);
    return () => window.clearTimeout(timer);
  }, [draft, loaded, receipt]);

  // Keep "saved N minutes ago" fresh.
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(timer);
  }, []);

  // Highlight the section in view.
  useEffect(() => {
    const blocks = document.querySelectorAll<HTMLElement>("[data-section]");
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setCurrent(visible[0].target.getAttribute("data-section") as SectionId);
      },
      { rootMargin: "-30% 0px -60% 0px" },
    );
    blocks.forEach((b) => observer.observe(b));
    return () => observer.disconnect();
  }, [receipt]);

  const set = useCallback(
    <K extends keyof ListingDraft>(key: K, value: ListingDraft[K]) =>
      setDraft((d) => ({ ...d, [key]: value })),
    [],
  );

  const errors = useMemo(
    () =>
      Object.fromEntries(SECTIONS.map((s) => [s.id, sectionErrors(s.id, draft, photos.length)])) as Record<
        SectionId,
        Record<string, string>
      >,
    [draft, photos.length],
  );
  const isComplete = (id: SectionId) => Object.keys(errors[id]).length === 0;
  const completed = SECTIONS.filter((s) => isComplete(s.id)).length;
  const percent = Math.round((completed / SECTIONS.length) * 100);
  const err = (id: SectionId, field: string) => (showErrors ? errors[id][field] : undefined);

  const goTo = (id: SectionId) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setShowErrors(true);
    setFormError("");
    const missing = SECTIONS.find((s) => s.required && !isComplete(s.id));
    if (missing) {
      setFormError(`Some required answers are missing, starting with “${missing.title}”.`);
      goTo(missing.id);
      return;
    }

    setPending(true);
    try {
      const result = await submitListing({
        full_name: draft.contactName.trim(),
        phone_number: toE164(draft.contactCountry, draft.contactPhone),
        email: account.email || undefined,
        message: composeMessage(draft, photos.length),
      });
      clearDraft();
      setReceipt(result);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      const state = formStateFromError(error);
      const fieldMessage = Object.values(state.fieldErrors).flat()[0];
      setFormError(state.formError || fieldMessage || "The listing could not be sent. Please try again.");
    } finally {
      setPending(false);
    }
  };

  const onSaveAndExit = () => {
    writeDraft(draft);
    router.push(routes.account.root);
  };

  const pricing = pricingCopy(draft.listingType);

  if (receipt) {
    return (
      <div className={styles.layout}>
        <div className={styles.success}>
          <span className={styles.successIcon} aria-hidden="true">
            <CheckIcon size={22} />
          </span>
          <h2 className={styles.successTitle}>Submitted for review</h2>
          <p className={styles.successText}>
            Thank you. An advisor will review <strong>{draft.name}</strong> and call you on{" "}
            {toE164(draft.contactCountry, draft.contactPhone)}, usually within two working days.
            {photos.length ? " They will ask you to send the photos you selected." : ""}
          </p>
          <p className={styles.successRef}>Reference {receipt.id.slice(0, 8).toUpperCase()}</p>
          <div className={styles.successActions}>
            <GoldButton href={routes.account.root}>Back to my account</GoldButton>
            <Link href={routes.buy} className={styles.ghostDark}>
              Browse the collection
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form className={styles.layout} onSubmit={onSubmit} noValidate>
      <aside className={styles.side} aria-label="Progress">
        <div className={styles.sideCard}>
          <div className={styles.sideTop}>
            <span className={styles.sideTitle}>Your progress</span>
            <span className={styles.sidePct}>{percent}%</span>
          </div>
          <div
            className={styles.barTrack}
            role="progressbar"
            aria-valuenow={percent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Sections complete"
          >
            <span className={styles.barFill} style={{ width: `${percent}%` }} />
          </div>
          <ol className={styles.steps}>
            {SECTIONS.map((section, index) => {
              const done = isComplete(section.id);
              const isCurrent = current === section.id;
              return (
                <li key={section.id}>
                  <button
                    type="button"
                    onClick={() => goTo(section.id)}
                    className={`${styles.step} ${done ? styles.stepDone : ""} ${isCurrent ? styles.stepCurrent : ""}`}
                    aria-current={isCurrent ? "step" : undefined}
                  >
                    <span className={styles.stepMark}>
                      {done && !isCurrent ? <CheckIcon /> : String(index + 1).padStart(2, "0")}
                    </span>
                    <span className={styles.stepName}>{section.title}</span>
                  </button>
                </li>
              );
            })}
          </ol>
        </div>

        <div className={styles.helpCard}>
          <p className={styles.helpTitle}>Need a hand?</p>
          <p className={styles.helpText}>An advisor can fill this in with you over a short call.</p>
          <Link href={`${routes.contact}?topic=listing` as Route} className={styles.helpLink}>
            Book a call
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M3.5 8H12.5M12.5 8L8.5 4M12.5 8L8.5 12" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Link>
        </div>
      </aside>

      <div className={styles.form}>
        {/* 01 Listing type */}
        <FormBlock id="listing-type" marker="01" title={SECTIONS[0]!.title} description={SECTIONS[0]!.description} optional={!SECTIONS[0]!.required} complete={isComplete("listing-type")} current={current === "listing-type"}>
          <Field label="What would you like to do?" asGroup className={fieldWidth.full}>
            <OptionCards
              name="listingType"
              value={draft.listingType}
              onChange={(v) => set("listingType", v)}
              options={LISTING_TYPES.map((t) => ({ ...t, icon: TYPE_ICONS[t.value] }))}
            />
          </Field>
          <Field label="Property type" htmlFor="lp-type" className={fieldWidth.half} error={err("listing-type", "propertyType")}>
            <Select
              id="lp-type"
              value={draft.propertyType}
              onChange={(e) => set("propertyType", e.target.value)}
              placeholder="Choose a type"
              options={PROPERTY_TYPES}
              invalid={Boolean(err("listing-type", "propertyType"))}
            />
          </Field>
          <Field label="Category label" optional htmlFor="lp-label" className={fieldWidth.half}>
            <Select
              id="lp-label"
              value={draft.categoryLabel}
              onChange={(e) => set("categoryLabel", e.target.value)}
              placeholder="e.g. New, Exclusive"
              options={CATEGORY_LABELS}
            />
          </Field>
        </FormBlock>

        {/* 02 Location */}
        <FormBlock id="location" marker="02" title={SECTIONS[1]!.title} description={SECTIONS[1]!.description} optional={!SECTIONS[1]!.required} complete={isComplete("location")} current={current === "location"}>
          <Field label="Street address" htmlFor="lp-street" className={fieldWidth.full} error={err("location", "street")}>
            <TextInput
              id="lp-street"
              autoComplete="street-address"
              value={draft.street}
              onChange={(e) => set("street", e.target.value)}
              placeholder="Street and number"
              leading={<PinIcon />}
              invalid={Boolean(err("location", "street"))}
            />
          </Field>
          <Field label="City" htmlFor="lp-city" className={fieldWidth.half} error={err("location", "city")}>
            <TextInput
              id="lp-city"
              autoComplete="address-level2"
              value={draft.city}
              onChange={(e) => set("city", e.target.value)}
              placeholder="City"
              invalid={Boolean(err("location", "city"))}
            />
          </Field>
          <Field label="Country" htmlFor="lp-country" className={fieldWidth.half} error={err("location", "country")}>
            <Select
              id="lp-country"
              value={draft.country}
              onChange={(e) => set("country", e.target.value)}
              placeholder="Choose a country"
              options={COUNTRIES}
              invalid={Boolean(err("location", "country"))}
            />
          </Field>
        </FormBlock>

        {/* 03 Property details */}
        <FormBlock id="details" marker="03" title={SECTIONS[2]!.title} description={SECTIONS[2]!.description} optional={!SECTIONS[2]!.required} complete={isComplete("details")} current={current === "details"}>
          <Field
            label="Property name"
            htmlFor="lp-name"
            className={fieldWidth.full}
            hint="Shown as the title on the listing card."
            error={err("details", "name")}
          >
            <TextInput
              id="lp-name"
              value={draft.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="e.g. Casa del Acantilado"
              invalid={Boolean(err("details", "name"))}
            />
          </Field>
          <Field label="Bedrooms" className={fieldWidth.half}>
            <Stepper label="Bedrooms" value={draft.bedrooms} onChange={(v) => set("bedrooms", v)} max={30} />
          </Field>
          <Field label="Bathrooms" className={fieldWidth.half}>
            <Stepper label="Bathrooms" value={draft.bathrooms} onChange={(v) => set("bathrooms", v)} max={30} />
          </Field>
          <Field label="Interior size" htmlFor="lp-size" className={fieldWidth.half} error={err("details", "size")}>
            <TextInput
              id="lp-size"
              inputMode="numeric"
              value={draft.size}
              onChange={(e) => set("size", groupDigits(e.target.value))}
              placeholder="0"
              boxClassName={styles.unitBox}
              invalid={Boolean(err("details", "size"))}
              trailing={
                <Segmented
                  label="Unit"
                  value={draft.sizeUnit}
                  onChange={(v) => set("sizeUnit", v)}
                  options={[
                    { value: "sqft", label: "sq ft" },
                    { value: "m2", label: "m²" },
                  ]}
                />
              }
            />
          </Field>
          <Field label="Year built" optional htmlFor="lp-year" className={fieldWidth.half} error={err("details", "yearBuilt")}>
            <TextInput
              id="lp-year"
              inputMode="numeric"
              maxLength={4}
              value={draft.yearBuilt}
              onChange={(e) => set("yearBuilt", e.target.value.replace(/\D/g, ""))}
              placeholder="e.g. 2019"
              invalid={Boolean(err("details", "yearBuilt"))}
            />
          </Field>
        </FormBlock>

        {/* 04 Features */}
        <FormBlock id="features" marker="04" title={SECTIONS[3]!.title} description={SECTIONS[3]!.description} optional={!SECTIONS[3]!.required} complete={isComplete("features")} current={current === "features"}>
          <Field label="Amenities" asGroup className={fieldWidth.full}>
            <ChipGroup
              name="amenities"
              multiple
              options={AMENITIES.map((a) => ({ value: a, label: a }))}
              selected={draft.amenities}
              onToggle={(amenity) =>
                set(
                  "amenities",
                  draft.amenities.includes(amenity)
                    ? draft.amenities.filter((a) => a !== amenity)
                    : [...draft.amenities, amenity],
                )
              }
            />
          </Field>
          <Field label="Furnishing" asGroup className={fieldWidth.full}>
            <ToggleRow
              title={pricing.furnished}
              description={pricing.furnishedDesc}
              checked={draft.furnished}
              onChange={(v) => set("furnished", v)}
            />
          </Field>
        </FormBlock>

        {/* 05 Description */}
        <FormBlock id="description" marker="05" title={SECTIONS[4]!.title} description={SECTIONS[4]!.description} optional={!SECTIONS[4]!.required} complete={isComplete("description")} current={current === "description"}>
          <Field label="About the property" htmlFor="lp-desc" className={fieldWidth.full} error={err("description", "description")}>
            <TextArea
              id="lp-desc"
              value={draft.description}
              onChange={(v) => set("description", v)}
              max={DESCRIPTION_MAX}
              placeholder="What is it like to arrive, to wake up there, to spend an evening on the terrace?"
              invalid={Boolean(err("description", "description"))}
            />
          </Field>
        </FormBlock>

        {/* 06 Photos */}
        <FormBlock id="photos" marker="06" title={SECTIONS[5]!.title} description={SECTIONS[5]!.description} optional={!SECTIONS[5]!.required} complete={isComplete("photos")} current={current === "photos"}>
          <Field label="Gallery" asGroup className={fieldWidth.full} hint="Photos stay on this device until an advisor collects them after review.">
            <PhotoUpload photos={photos} onChange={setPhotos} />
          </Field>
        </FormBlock>

        {/* 07 Pricing & availability */}
        <FormBlock id="pricing" marker="07" title={SECTIONS[6]!.title} description={SECTIONS[6]!.description} optional={!SECTIONS[6]!.required} complete={isComplete("pricing")} current={current === "pricing"}>
          <Field label={pricing.label} htmlFor="lp-price" className={fieldWidth.half} error={err("pricing", "price")}>
            <TextInput
              id="lp-price"
              inputMode="numeric"
              value={draft.price}
              onChange={(e) => set("price", groupDigits(e.target.value))}
              placeholder="0"
              disabled={draft.priceOnRequest}
              invalid={Boolean(err("pricing", "price"))}
              leading={
                <span className={styles.currency}>
                  <span className={styles.currencySymbol} aria-hidden="true">
                    {CURRENCIES.find((c) => c.value === draft.currency)?.label}
                  </span>
                  <svg width="14" height="14" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <select
                    className={styles.currencySelect}
                    value={draft.currency}
                    onChange={(e) => set("currency", e.target.value)}
                    aria-label="Currency"
                  >
                    {CURRENCIES.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.value} ({c.label})
                      </option>
                    ))}
                  </select>
                </span>
              }
              trailing={<span className={styles.suffix}>{pricing.suffix}</span>}
            />
          </Field>
          <Field label="Available from" htmlFor="lp-date" className={fieldWidth.half} error={err("pricing", "availableFrom")}>
            <TextInput
              id="lp-date"
              type="date"
              value={draft.availableFrom}
              min={new Date().toISOString().slice(0, 10)}
              onChange={(e) => set("availableFrom", e.target.value)}
              invalid={Boolean(err("pricing", "availableFrom"))}
            />
          </Field>
          <Field label="Visibility" asGroup className={fieldWidth.full}>
            <ToggleRow
              title="Price on request"
              description="Hide the price and let people contact an advisor instead."
              checked={draft.priceOnRequest}
              onChange={(v) => set("priceOnRequest", v)}
            />
          </Field>
        </FormBlock>

        {/* 08 Contact */}
        <FormBlock id="contact" marker="08" title={SECTIONS[7]!.title} description={SECTIONS[7]!.description} optional={!SECTIONS[7]!.required} complete={isComplete("contact")} current={current === "contact"}>
          <Field label="Full name" htmlFor="lp-contact-name" className={fieldWidth.half} error={err("contact", "contactName")}>
            <TextInput
              id="lp-contact-name"
              autoComplete="name"
              value={draft.contactName}
              onChange={(e) => set("contactName", e.target.value)}
              placeholder="Your name"
              invalid={Boolean(err("contact", "contactName"))}
            />
          </Field>
          <Field label="Phone number" htmlFor="lp-contact-phone" className={fieldWidth.half} error={err("contact", "contactPhone")}>
            <PhoneInput
              id="lp-contact-phone"
              country={draft.contactCountry}
              onCountryChange={(v) => set("contactCountry", v)}
              value={draft.contactPhone}
              onChange={(e) => set("contactPhone", e.target.value)}
              placeholder="721 234 567"
              invalid={Boolean(err("contact", "contactPhone"))}
            />
          </Field>
        </FormBlock>

        <FormAlert>{formError}</FormAlert>

        <div className={styles.actions}>
          <span className={styles.saved} aria-live="polite">
            <span className={styles.savedDot} aria-hidden="true" />
            {savedAt ? `Draft saved ${relativeTime(savedAt, now)}` : "Your answers save automatically"}
          </span>
          <div className={styles.actionsBtns}>
            <button type="button" className={styles.ghost} onClick={onSaveAndExit}>
              Save and exit
            </button>
            <GoldButton loading={pending}>Submit for review</GoldButton>
          </div>
        </div>
      </div>
    </form>
  );
}
