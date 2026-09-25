import type { Route } from "next";
import Image from "next/image";

import { ButtonLink } from "@/components/ui/ButtonLink";

import styles from "./Hero.module.css";

interface HeroProps {
  eyebrow: string;
  title: string;
  description: string;
  action: { label: string; href: Route };
  image: { src: string; alt: string };
  caption?: string;
}

export function Hero({ eyebrow, title, description, action, image, caption }: HeroProps) {
  return (
    <section className={styles.hero}>
      <Image
        src={image.src}
        alt={image.alt}
        fill
        priority
        sizes="100vw"
        className={styles.photo}
      />
      <div className={styles.veil} aria-hidden="true" />

      <div className={styles.copy}>
        <p className={styles.eyebrow}>{eyebrow}</p>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.description}>{description}</p>
      </div>

      <div className={styles.footer}>
        <ButtonLink href={action.href} variant="accent">
          {action.label}
        </ButtonLink>
        {caption ? <p className={styles.caption}>{caption}</p> : null}
      </div>
    </section>
  );
}
