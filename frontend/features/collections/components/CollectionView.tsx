import Link from "next/link";

import { ListingCard } from "@/components/shared/ListingCard";
import { ButtonLink } from "@/components/ui/ButtonLink";

import {
  filterListings,
  isFiltered,
  PAGE_SIZE,
  parseQuery,
  queryHref,
  SORTS,
  type SearchParams,
} from "../query";
import type { Collection } from "../types";

import styles from "./CollectionView.module.css";
import { SearchBar, type FilterField } from "./SearchBar";
import { SortMenu } from "./SortMenu";

/**
 * A collection page body: introduction, search and filters, quick-filter
 * chips, results and "load more". Everything is derived from the query string
 * on the server; the client parts only navigate.
 */

export function CollectionView({
  collection,
  searchParams,
}: {
  collection: Collection;
  searchParams: SearchParams;
}) {
  const query = parseQuery(collection, searchParams);
  const results = filterListings(collection, query);
  const visible = results.slice(0, query.page * PAGE_SIZE);
  const href = (changes: Parameters<typeof queryHref>[2]) =>
    queryHref(collection.path, query, changes);

  const fields: FilterField[] = collection.filters.map((filter) =>
    filter.kind === "dates"
      ? { kind: "dates", label: filter.label }
      : { kind: filter.kind, param: filter.param, label: filter.label, options: filter.options },
  );

  const chips = [{ value: "", label: "All" }, ...collection.chips];
  const currentSort = SORTS.find((s) => s.value === query.sort)!;

  return (
    <>
      <section className={styles.intro}>
        <div className={styles.heading}>
          <p className={styles.eyebrow}>{collection.eyebrow}</p>
          <h1 className={styles.title}>{collection.title}</h1>
        </div>
        <p className={styles.introduction}>{collection.introduction}</p>
      </section>

      <section className={styles.filterRegion} aria-label="Search and filters">
        <SearchBar
          key={JSON.stringify(query)}
          path={collection.path}
          fields={fields}
          query={query}
        />

        <nav className={styles.chips} aria-label="Quick filters">
          {chips.map((chip) => {
            const active = query.chip === chip.value;
            return (
              <Link
                key={chip.value || "all"}
                href={href({ chip: chip.value, page: 1 })}
                scroll={false}
                className={`${styles.chip} ${active ? styles.chipActive : ""}`}
                aria-current={active ? "true" : undefined}
              >
                {chip.label}
              </Link>
            );
          })}
        </nav>
      </section>

      <section className={styles.results} aria-label="Results">
        <div className={styles.resultsHeader}>
          <p className={styles.count} aria-live="polite">
            {results.length} exceptional {results.length === 1 ? "place" : "places"}
          </p>
          <SortMenu
            current={currentSort.label}
            items={SORTS.map((sort) => ({
              label: sort.label,
              href: href({ sort: sort.value, page: 1 }),
              active: sort.value === query.sort,
            }))}
          />
        </div>

        {visible.length ? (
          <ul className={styles.grid}>
            {visible.map((listing) => (
              <li key={listing.id}>
                <ListingCard listing={listing} />
              </li>
            ))}
          </ul>
        ) : (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>Nothing matches these filters.</p>
            <p>Try a wider search, or let our advisors look off-market for you.</p>
            {isFiltered(query) ? (
              <Link href={collection.path} className={styles.emptyReset}>
                Clear all filters
              </Link>
            ) : null}
          </div>
        )}

        {visible.length < results.length ? (
          <div className={styles.loadMore}>
            <ButtonLink href={href({ page: query.page + 1 })} scroll={false}>
              Load more properties
            </ButtonLink>
          </div>
        ) : null}
      </section>
    </>
  );
}
