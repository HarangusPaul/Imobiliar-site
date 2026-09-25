"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";

import { Popover } from "@/components/ui/Popover";
import { ArrowRight } from "@/components/ui/icons";

import { queryHref, type CollectionQuery } from "../query";
import type { FilterOption } from "../types";

import styles from "./SearchBar.module.css";

/**
 * Search input, filter dropdowns and the search button.
 *
 * It is a real GET form, so it works before hydration; with JavaScript the
 * submit is intercepted to build a clean URL (no empty parameters) and
 * navigate client-side. Remount it with a `key` when the query changes.
 */

/** The serialisable part of a filter; match functions stay on the server. */
export type FilterField =
  | { kind: "choice"; param: string; label: string; options: FilterOption[] }
  | { kind: "features"; param: string; label: string; options: FilterOption[] }
  | { kind: "dates"; label: string };

interface SearchBarProps {
  path: string;
  fields: FilterField[];
  query: CollectionQuery;
}

function Chevron() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M3 4.5 6 7.5 9 4.5" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="5.25" stroke="currentColor" strokeWidth="1.4" />
      <path d="m12 12 3.5 3.5" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

const shortDate = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", { day: "numeric", month: "short" });

export function SearchBar({ path, fields, query }: SearchBarProps) {
  const router = useRouter();
  const [q, setQ] = useState(query.q);
  const [choices, setChoices] = useState(query.choices);
  const [features, setFeatures] = useState(query.features);
  const [checkIn, setCheckIn] = useState(query.checkIn);
  const [checkOut, setCheckOut] = useState(query.checkOut);
  const [openKey, setOpenKey] = useState<string | null>(null);

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setOpenKey(null);
    router.push(
      queryHref(path, { ...query, q: q.trim(), choices, features, checkIn, checkOut, page: 1 }),
    );
  };

  const setChoice = (param: string, value: string) => {
    setChoices((current) => {
      const next = { ...current };
      if (value) next[param] = value;
      else delete next[param];
      return next;
    });
    setOpenKey(null);
  };

  const toggleFeature = (value: string) =>
    setFeatures((current) =>
      current.includes(value) ? current.filter((v) => v !== value) : [...current, value],
    );

  const renderField = (field: FilterField) => {
    const key = field.kind === "dates" ? "dates" : field.param;
    let label = field.label;
    let active = false;
    let panel: ReactNode;

    if (field.kind === "choice") {
      const selected = field.options.find((o) => o.value === choices[field.param]);
      if (selected) [label, active] = [selected.label, true];
      panel = (
        <fieldset className={styles.options}>
          <legend className={styles.legend}>{field.label}</legend>
          {[{ value: "", label: "Any" }, ...field.options].map((option) => (
            <label key={option.value || "any"} className={styles.option}>
              <input
                type="radio"
                name={field.param}
                value={option.value}
                checked={(choices[field.param] ?? "") === option.value}
                onChange={() => setChoice(field.param, option.value)}
              />
              {option.label}
            </label>
          ))}
        </fieldset>
      );
    } else if (field.kind === "features") {
      if (features.length) [label, active] = [`${field.label} · ${features.length}`, true];
      panel = (
        <fieldset className={styles.options}>
          <legend className={styles.legend}>{field.label}</legend>
          {field.options.map((option) => (
            <label key={option.value} className={styles.option}>
              <input
                type="checkbox"
                name={field.param}
                value={option.value}
                checked={features.includes(option.value)}
                onChange={() => toggleFeature(option.value)}
              />
              {option.label}
            </label>
          ))}
          {features.length ? (
            <button type="button" className={styles.clear} onClick={() => setFeatures([])}>
              Clear
            </button>
          ) : null}
        </fieldset>
      );
    } else {
      if (checkIn || checkOut) {
        active = true;
        label = [checkIn, checkOut].filter(Boolean).map(shortDate).join(" – ");
      }
      panel = (
        <div className={styles.dates}>
          <label className={styles.dateField}>
            Check-in
            <input
              type="date"
              name="checkin"
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
            />
          </label>
          <label className={styles.dateField}>
            Check-out
            <input
              type="date"
              name="checkout"
              min={checkIn || undefined}
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
            />
          </label>
        </div>
      );
    }

    return (
      <div key={key} className={styles.filter}>
        <Popover
          open={openKey === key}
          onOpenChange={(open) => setOpenKey(open ? key : null)}
          triggerClassName={`${styles.trigger} ${active ? styles.triggerActive : ""}`}
          trigger={
            <>
              <span className={styles.triggerLabel}>{label}</span>
              <Chevron />
            </>
          }
        >
          {panel}
        </Popover>
      </div>
    );
  };

  return (
    <form action={path} method="get" role="search" className={styles.bar} onSubmit={onSubmit}>
      <label className={styles.search}>
        <SearchIcon />
        <span className="visually-hidden">Search</span>
        <input
          type="search"
          name="q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search city, area or property"
          className={styles.input}
        />
      </label>

      <div className={styles.filters}>{fields.map(renderField)}</div>

      {query.chip ? <input type="hidden" name="chip" value={query.chip} /> : null}
      {query.sort !== "featured" ? <input type="hidden" name="sort" value={query.sort} /> : null}

      <button type="submit" className={styles.submit}>
        Search
        <ArrowRight size={16} />
      </button>
    </form>
  );
}
