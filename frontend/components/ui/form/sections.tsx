"use client";

import type { ReactNode } from "react";

import { CheckIcon } from "./controls";
import styles from "./sections.module.css";

/**
 * Larger form building blocks: the white section card, option cards, chip
 * groups and a counted textarea. Generic; the copy comes from the caller.
 */

/** Width helpers for fields laid out inside a `FormBlock` body. */
export const fieldWidth = { full: styles.q, half: styles.qHalf };

// ---- Block ------------------------------------------------------------------

interface FormBlockProps {
  id: string;
  /** The square marker: a number like "03" or an icon. */
  marker: ReactNode;
  title: string;
  description?: string;
  optional?: boolean;
  complete?: boolean;
  current?: boolean;
  /** Rendered below the body, above a divider (e.g. consent + submit). */
  footer?: ReactNode;
  children: ReactNode;
}

export function FormBlock({
  id,
  marker,
  title,
  description,
  optional,
  complete,
  current,
  footer,
  children,
}: FormBlockProps) {
  return (
    <section
      id={id}
      data-section={id}
      className={`${styles.block} ${current ? styles.blockCurrent : ""}`}
      aria-labelledby={`${id}-title`}
    >
      <div className={styles.head}>
        <span className={styles.marker} aria-hidden="true">
          {marker}
        </span>
        <div className={styles.titles}>
          <h2 id={`${id}-title`} className={styles.title}>
            {title}
            {optional ? <span className={styles.optional}>Optional</span> : null}
          </h2>
          {description ? <p className={styles.desc}>{description}</p> : null}
        </div>
        {complete ? (
          <span className={styles.done}>
            <CheckIcon /> Complete
          </span>
        ) : null}
      </div>
      <div className={styles.body}>{children}</div>
      {footer ? <div className={styles.footer}>{footer}</div> : null}
    </section>
  );
}

// ---- Option cards -----------------------------------------------------------

export interface OptionCard<T extends string> {
  value: T;
  title: string;
  description: string;
  /** SVG children drawn in a 24x24 viewBox. */
  icon: ReactNode;
}

export function OptionCards<T extends string>({
  name,
  value,
  options,
  onChange,
}: {
  name: string;
  value: T;
  options: OptionCard<T>[];
  onChange: (value: T) => void;
}) {
  return (
    <div className={styles.optCards}>
      {options.map((option) => {
        const on = value === option.value;
        return (
          <label key={option.value} className={`${styles.optCard} ${on ? styles.optCardOn : ""}`}>
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={on}
              onChange={() => onChange(option.value)}
              className="visually-hidden"
            />
            <span className={styles.optIcon} aria-hidden="true">
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                {option.icon}
              </svg>
            </span>
            <span className={styles.optTitle}>{option.title}</span>
            <span className={styles.optDesc}>{option.description}</span>
            <span className={styles.radio} aria-hidden="true">
              {on ? <span className={styles.radioDot} /> : null}
            </span>
          </label>
        );
      })}
    </div>
  );
}

// ---- Chips ------------------------------------------------------------------

/** Pill toggles. `multiple` makes them checkboxes, otherwise radios. */
export function ChipGroup({
  name,
  options,
  selected,
  onToggle,
  multiple = false,
}: {
  name: string;
  options: Array<{ value: string; label: string }>;
  selected: string[];
  onToggle: (value: string) => void;
  multiple?: boolean;
}) {
  return (
    <div className={styles.chips}>
      {options.map((option) => {
        const on = selected.includes(option.value);
        return (
          <label key={option.value} className={`${styles.chip} ${on ? styles.chipOn : ""}`}>
            <input
              type={multiple ? "checkbox" : "radio"}
              name={name}
              value={option.value}
              className="visually-hidden"
              checked={on}
              onChange={() => onToggle(option.value)}
            />
            {on ? (
              <span className={styles.chipCheck} aria-hidden="true">
                <CheckIcon />
              </span>
            ) : null}
            {option.label}
          </label>
        );
      })}
    </div>
  );
}

// ---- Textarea ---------------------------------------------------------------

export function TextArea({
  id,
  value,
  onChange,
  max,
  placeholder,
  invalid,
  rows = 5,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  max: number;
  placeholder?: string;
  invalid?: boolean;
  rows?: number;
}) {
  return (
    <div className={`${styles.area} ${invalid ? styles.areaInvalid : ""}`}>
      <textarea
        id={id}
        value={value}
        maxLength={max}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-invalid={invalid || undefined}
        className={styles.areaText}
        rows={rows}
      />
      <span className={styles.areaCount} aria-live="polite">
        {value.length} / {max}
      </span>
    </div>
  );
}
