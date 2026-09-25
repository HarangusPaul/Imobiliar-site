import type { Route } from "next";
import Image from "next/image";
import Link from "next/link";

import styles from "./ListingCard.module.css";

/**
 * The editorial listing card: photo with a tag, then location, name, facts and
 * rate. It takes display-ready strings so the curated collections and
 * API-backed lists can both feed it; formatting a price belongs to whoever
 * builds the data. Without an `href` the card is not a link.
 */

export interface ListingCardData {
  id: string;
  href?: Route;
  tag: string;
  location: string;
  name: string;
  facts: string;
  rate: string;
  image: { src: string; alt: string };
}

export function ListingCard({ listing }: { listing: ListingCardData }) {
  const body = (
    <>
      <div className={styles.media}>
        <Image
          src={listing.image.src}
          alt={listing.image.alt}
          fill
          sizes="(max-width: 640px) 90vw, (max-width: 1024px) 45vw, 427px"
          className={styles.photo}
        />
        <span className={styles.tag}>{listing.tag}</span>
      </div>

      <div className={styles.details}>
        <p className={styles.location}>{listing.location}</p>
        <h3 className={styles.name}>{listing.name}</h3>
        <div className={styles.facts}>
          <span>{listing.facts}</span>
          <strong className={styles.rate}>{listing.rate}</strong>
        </div>
      </div>
    </>
  );

  return (
    <article className={styles.card}>
      {listing.href ? (
        <Link href={listing.href} className={`${styles.body} ${styles.link}`}>
          {body}
        </Link>
      ) : (
        <div className={styles.body}>{body}</div>
      )}
    </article>
  );
}
