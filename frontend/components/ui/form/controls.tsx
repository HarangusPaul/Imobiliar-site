"use client";

import Link from "next/link";
import type { Route } from "next";
import {
  useId,
  useState,
  type ButtonHTMLAttributes,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
} from "react";

import styles from "./form.module.css";

/**
 * Form controls in the Monument style: soft inset fields with a gold focus
 * ring, pill switches and a metallic primary button. Generic by rule - no
 * domain vocabulary here.
 */

// ---- Icons ------------------------------------------------------------------

export function CheckIcon({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path
        d="M2.5 6.25L5 8.5L9.5 3.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function ChevronIcon({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path
        d="M3 4.5L6 7.5L9 4.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M3.5 8H12.5M12.5 8L8.5 4M12.5 8L8.5 12"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ---- Field wrapper ----------------------------------------------------------

interface FieldProps {
  label: ReactNode;
  htmlFor?: string;
  optional?: boolean;
  aside?: ReactNode;
  hint?: ReactNode;
  error?: string;
  className?: string;
  children: ReactNode;
  /** Render the label as a legend for groups of controls. */
  asGroup?: boolean;
}

export function Field({
  label,
  htmlFor,
  optional,
  aside,
  hint,
  error,
  className,
  children,
  asGroup,
}: FieldProps) {
  const labelContent = (
    <>
      <span className={styles.labelText}>
        {label}
        {optional ? <span className={styles.optional}>Optional</span> : null}
      </span>
      {aside}
    </>
  );

  if (asGroup) {
    return (
      <fieldset className={`${styles.field} ${styles.group} ${className ?? ""}`}>
        <legend className={styles.label}>{labelContent}</legend>
        {children}
        {hint && !error ? <p className={styles.hint}>{hint}</p> : null}
        {error ? <p className={styles.error}>{error}</p> : null}
      </fieldset>
    );
  }

  return (
    <div className={`${styles.field} ${className ?? ""}`}>
      <div className={styles.label}>
        {htmlFor ? (
          <label htmlFor={htmlFor} className={styles.labelText}>
            {label}
            {optional ? <span className={styles.optional}>Optional</span> : null}
          </label>
        ) : (
          <span className={styles.labelText}>{label}</span>
        )}
        {aside}
      </div>
      {children}
      {hint && !error ? <p className={styles.hint}>{hint}</p> : null}
      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

// ---- Text input -------------------------------------------------------------

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  leading?: ReactNode;
  trailing?: ReactNode;
  invalid?: boolean;
  boxClassName?: string;
}

export function TextInput({
  leading,
  trailing,
  invalid,
  boxClassName,
  className,
  ...props
}: TextInputProps) {
  return (
    <div className={`${styles.box} ${invalid ? styles.boxInvalid : ""} ${boxClassName ?? ""}`}>
      {leading}
      <input
        {...props}
        aria-invalid={invalid || undefined}
        className={`${styles.input} ${className ?? ""}`}
      />
      {trailing}
    </div>
  );
}

// ---- Password ---------------------------------------------------------------

function LockIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <rect x="3" y="8" width="12" height="8" rx="2.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5.75 8V5.75a3.25 3.25 0 0 1 6.5 0V8" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

function EyeIcon({ off }: { off: boolean }) {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path
        d="M1.5 9S4.25 3.75 9 3.75 16.5 9 16.5 9 13.75 14.25 9 14.25 1.5 9 1.5 9z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <circle cx="9" cy="9" r="2.25" stroke="currentColor" strokeWidth="1.5" />
      {off ? <path d="M3 15 15 3" stroke="currentColor" strokeWidth="1.5" /> : null}
    </svg>
  );
}

export function PasswordInput(props: Omit<TextInputProps, "type" | "leading" | "trailing">) {
  const [visible, setVisible] = useState(false);
  return (
    <TextInput
      {...props}
      type={visible ? "text" : "password"}
      leading={
        <span className={styles.icon}>
          <LockIcon />
        </span>
      }
      trailing={
        <button
          type="button"
          className={styles.iconButton}
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide password" : "Show password"}
          aria-pressed={visible}
        >
          <EyeIcon off={visible} />
        </button>
      }
    />
  );
}

// ---- Phone ------------------------------------------------------------------

export interface CountryCode {
  iso: string;
  dial: string;
  name: string;
}

export const COUNTRY_CODES: CountryCode[] = [
  { iso: "RO", dial: "+40", name: "Romania" },
  { iso: "UK", dial: "+44", name: "United Kingdom" },
  { iso: "US", dial: "+1", name: "United States" },
  { iso: "FR", dial: "+33", name: "France" },
  { iso: "DE", dial: "+49", name: "Germany" },
  { iso: "ES", dial: "+34", name: "Spain" },
  { iso: "IT", dial: "+39", name: "Italy" },
  { iso: "PT", dial: "+351", name: "Portugal" },
  { iso: "GR", dial: "+30", name: "Greece" },
  { iso: "NL", dial: "+31", name: "Netherlands" },
];

/** Country dial code plus local number. `toE164` joins them for submission. */
export function PhoneInput({
  country,
  onCountryChange,
  invalid,
  ...props
}: Omit<TextInputProps, "type" | "leading"> & {
  country: string;
  onCountryChange: (iso: string) => void;
}) {
  const selected = COUNTRY_CODES.find((c) => c.iso === country) ?? COUNTRY_CODES[0]!;
  return (
    <TextInput
      {...props}
      type="tel"
      inputMode="tel"
      autoComplete="tel-national"
      invalid={invalid}
      leading={
        <span className={styles.cc}>
          <span className={styles.ccBadge} aria-hidden="true">
            {selected.iso}
          </span>
          <span className={styles.ccCode} aria-hidden="true">
            {selected.dial}
          </span>
          <ChevronIcon />
          <select
            className={styles.ccSelect}
            value={selected.iso}
            onChange={(e) => onCountryChange(e.target.value)}
            aria-label="Country code"
          >
            {COUNTRY_CODES.map((c) => (
              <option key={c.iso} value={c.iso}>
                {c.name} ({c.dial})
              </option>
            ))}
          </select>
        </span>
      }
    />
  );
}

export function toE164(country: string, number: string): string {
  const dial = (COUNTRY_CODES.find((c) => c.iso === country) ?? COUNTRY_CODES[0]!).dial;
  const trimmed = number.trim();
  if (trimmed.startsWith("+")) return trimmed.replace(/[^\d+]/g, "");
  return dial + trimmed.replace(/\D/g, "").replace(/^0+/, "");
}

// ---- Select -----------------------------------------------------------------

export function Select({
  options,
  placeholder,
  invalid,
  className,
  ...props
}: Omit<SelectHTMLAttributes<HTMLSelectElement>, "children"> & {
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
  invalid?: boolean;
}) {
  return (
    <div className={`${styles.box} ${styles.selectBox} ${invalid ? styles.boxInvalid : ""}`}>
      <select
        {...props}
        aria-invalid={invalid || undefined}
        className={`${styles.select} ${props.value ? "" : styles.selectEmpty} ${className ?? ""}`}
      >
        {placeholder !== undefined ? <option value="">{placeholder}</option> : null}
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <span className={styles.selectChevron}>
        <ChevronIcon size={14} />
      </span>
    </div>
  );
}

// ---- Checkbox ---------------------------------------------------------------

export function Checkbox({
  checked,
  onChange,
  children,
  invalid,
  name,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  children: ReactNode;
  invalid?: boolean;
  name?: string;
}) {
  return (
    <label className={`${styles.check} ${invalid ? styles.checkInvalid : ""}`}>
      <input
        type="checkbox"
        name={name}
        className="visually-hidden"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className={`${styles.checkBox} ${checked ? styles.checkBoxOn : ""}`} aria-hidden="true">
        {checked ? <CheckIcon /> : null}
      </span>
      <span>{children}</span>
    </label>
  );
}

// ---- Toggle -----------------------------------------------------------------

export function ToggleRow({
  title,
  description,
  checked,
  onChange,
}: {
  title: ReactNode;
  description?: ReactNode;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  const id = useId();
  return (
    <div className={styles.toggleRow}>
      <div className={styles.toggleText}>
        <span id={`${id}-t`} className={styles.toggleTitle}>
          {title}
        </span>
        {description ? (
          <span id={`${id}-d`} className={styles.toggleDesc}>
            {description}
          </span>
        ) : null}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-labelledby={`${id}-t`}
        aria-describedby={description ? `${id}-d` : undefined}
        className={`${styles.switch} ${checked ? styles.switchOn : ""}`}
        onClick={() => onChange(!checked)}
      >
        <span className={styles.knob} />
      </button>
    </div>
  );
}

// ---- Stepper ----------------------------------------------------------------

export function Stepper({
  value,
  onChange,
  min = 0,
  max = 99,
  label,
}: {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  label: string;
}) {
  return (
    <div className={styles.stepper} role="group" aria-label={label}>
      <button
        type="button"
        className={styles.stepBtn}
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        aria-label={`Decrease ${label.toLowerCase()}`}
      >
        −
      </button>
      <output className={styles.stepVal} aria-live="polite">
        {value}
      </output>
      <button
        type="button"
        className={`${styles.stepBtn} ${styles.stepBtnOn}`}
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        aria-label={`Increase ${label.toLowerCase()}`}
      >
        +
      </button>
    </div>
  );
}

// ---- Segmented --------------------------------------------------------------

export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: Array<{ value: T; label: string }>;
  onChange: (value: T) => void;
  label: string;
}) {
  return (
    <span className={styles.segs} role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={value === o.value}
          className={`${styles.seg} ${value === o.value ? styles.segOn : ""}`}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </span>
  );
}

// ---- Gold primary button ----------------------------------------------------

type GoldButtonProps = {
  children: ReactNode;
  block?: boolean;
  loading?: boolean;
} & (
  | ({ href?: undefined } & ButtonHTMLAttributes<HTMLButtonElement>)
  | { href: Route }
);

export function GoldButton(props: GoldButtonProps) {
  const { children, block, loading } = props;
  const inner = (
    <>
      <span className={styles.gloss} aria-hidden="true" />
      <span className={styles.goldLabel}>{loading ? "Please wait…" : children}</span>
      <span className={styles.goldIcon}>
        {loading ? <span className={styles.spinner} aria-hidden="true" /> : <ArrowIcon />}
      </span>
    </>
  );

  if (props.href !== undefined) {
    return (
      <span className={`${styles.goldRing} ${block ? styles.goldBlock : ""}`}>
        <Link href={props.href} className={styles.gold}>
          {inner}
        </Link>
      </span>
    );
  }

  const { href: _href, block: _block, loading: _loading, children: _children, ...rest } = props;
  return (
    <span className={`${styles.goldRing} ${block ? styles.goldBlock : ""}`}>
      <button
        type="submit"
        {...rest}
        disabled={loading || rest.disabled}
        aria-busy={loading || undefined}
        className={styles.gold}
      >
        {inner}
      </button>
    </span>
  );
}

// ---- Form-level message -----------------------------------------------------

export function FormAlert({ children }: { children: ReactNode }) {
  if (!children) return null;
  return (
    <div className={styles.alert} role="alert">
      {children}
    </div>
  );
}

/** The inverse of `toE164`, for prefilling: longest matching dial code wins. */
export function splitE164(value: string): { country: string; number: string } {
  const match = [...COUNTRY_CODES]
    .sort((a, b) => b.dial.length - a.dial.length)
    .find((c) => value.startsWith(c.dial));
  return match
    ? { country: match.iso, number: value.slice(match.dial.length) }
    : { country: COUNTRY_CODES[0]!.iso, number: value };
}
