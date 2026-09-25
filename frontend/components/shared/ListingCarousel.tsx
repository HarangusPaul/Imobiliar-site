"use client";

import type { Route } from "next";
import { useCallback, useEffect, useRef, useState } from "react";

import { ButtonLink } from "@/components/ui/ButtonLink";
import { ArrowLeft, ArrowRight } from "@/components/ui/icons";

import { ListingCard, type ListingCardData } from "./ListingCard";
import styles from "./ListingCarousel.module.css";

/**
 * A numbered collection: heading, prev/next controls, a scroll-snapping row of
 * cards and a browse-all action. Scrolling is native, so touch and trackpad
 * work without the buttons; the buttons move by one card.
 */

interface ListingCarouselProps {
  index: string;
  title: string;
  listings: ListingCardData[];
  browse: { label: string; href: Route };
}

export function ListingCarousel({ index, title, listings, browse }: ListingCarouselProps) {
  const trackRef = useRef<HTMLUListElement>(null);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(false);
  const headingId = `collection-${index.replace(/\W+/g, "-")}`;

  const updateControls = useCallback(() => {
    const track = trackRef.current;
    if (!track) return;
    setCanPrev(track.scrollLeft > 1);
    setCanNext(track.scrollLeft + track.clientWidth < track.scrollWidth - 1);
  }, []);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    updateControls();
    track.addEventListener("scroll", updateControls, { passive: true });
    const observer = new ResizeObserver(updateControls);
    observer.observe(track);
    return () => {
      track.removeEventListener("scroll", updateControls);
      observer.disconnect();
    };
  }, [updateControls]);

  const scrollByCard = (direction: 1 | -1) => {
    const track = trackRef.current;
    const card = track?.firstElementChild as HTMLElement | null;
    if (!track || !card) return;
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    track.scrollBy({ left: direction * (card.offsetWidth + gap), behavior: "smooth" });
  };

  return (
    <section className={styles.section} aria-labelledby={headingId}>
      <div className={styles.heading}>
        <div className={styles.headingCopy}>
          <p className={styles.index}>{index}</p>
          <h2 id={headingId} className={styles.title}>
            {title}
          </h2>
        </div>

        <div className={styles.controls}>
          <button
            type="button"
            className={`${styles.control} ${styles.prev}`}
            onClick={() => scrollByCard(-1)}
            disabled={!canPrev}
            aria-label={`Previous ${title} listings`}
          >
            <ArrowLeft size={18} />
          </button>
          <button
            type="button"
            className={`${styles.control} ${styles.next}`}
            onClick={() => scrollByCard(1)}
            disabled={!canNext}
            aria-label={`Next ${title} listings`}
          >
            <ArrowRight size={18} />
          </button>
        </div>
      </div>

      <ul ref={trackRef} className={styles.track}>
        {listings.map((listing) => (
          <li key={listing.id} className={styles.slide}>
            <ListingCard listing={listing} />
          </li>
        ))}
      </ul>

      <div>
        <ButtonLink href={browse.href}>{browse.label}</ButtonLink>
      </div>
    </section>
  );
}
