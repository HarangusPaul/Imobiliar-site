import Image from "next/image";
import type { ReactNode } from "react";

import styles from "./AuthShell.module.css";

/**
 * The two-panel auth layout: a dark visual panel with copy and a featured
 * listing on the left, the form card on the right.
 */

interface AuthShellProps {
  eyebrow: string;
  title: string;
  text: string;
  feature: { location: string; name: string; note: string; image: string };
  children: ReactNode;
}

export function AuthShell({ eyebrow, title, text, feature, children }: AuthShellProps) {
  return (
    <div className={styles.page}>
      <section className={styles.visual}>
        <span className={styles.veil} aria-hidden="true" />
        <span className={styles.glow} aria-hidden="true" />
        <span className={styles.edge} aria-hidden="true" />

        <div className={styles.copy}>
          <p className={styles.eyebrow}>{eyebrow}</p>
          <p className={styles.title}>{title}</p>
          <p className={styles.text}>{text}</p>
        </div>

        <div className={styles.featureRing}>
          <div className={styles.feature}>
            <span className={styles.thumb}>
              <Image src={feature.image} alt="" fill sizes="84px" className={styles.thumbImg} />
            </span>
            <span className={styles.featureInfo}>
              <span className={styles.featureLoc}>{feature.location}</span>
              <span className={styles.featureName}>{feature.name}</span>
              <span className={styles.featureNote}>{feature.note}</span>
            </span>
          </div>
        </div>
      </section>

      <section className={styles.formSide}>
        <div className={styles.card}>{children}</div>
      </section>
    </div>
  );
}

export function AuthCardHead({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className={styles.cardHead}>
      <h1 className={styles.cardTitle}>{title}</h1>
      <p className={styles.cardSub}>{subtitle}</p>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
      <path d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z" fill="#4285F4" />
      <path d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.33-1.58-5.04-3.7H.96v2.33A9 9 0 0 0 9 18z" fill="#34A853" />
      <path d="M3.96 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.28-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3-2.33z" fill="#FBBC05" />
      <path d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58A9 9 0 0 0 .96 4.95l3 2.33C4.67 5.16 6.66 3.58 9 3.58z" fill="#EA4335" />
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg width="16" height="18" viewBox="0 0 16 18" aria-hidden="true">
      <path d="M13.2 9.56c-.02-2.02 1.65-3 1.72-3.04-.94-1.37-2.4-1.56-2.92-1.58-1.24-.13-2.43.73-3.06.73-.63 0-1.6-.71-2.64-.69A3.9 3.9 0 0 0 3 6.99c-1.41 2.44-.36 6.05 1.01 8.03.67.97 1.47 2.06 2.51 2.02 1.01-.04 1.39-.65 2.61-.65 1.22 0 1.56.65 2.63.63 1.09-.02 1.77-.99 2.43-1.96.77-1.12 1.08-2.21 1.1-2.27-.02-.01-2.1-.81-2.12-3.2zM11.2 3.62c.55-.67.93-1.6.83-2.53-.8.03-1.77.53-2.34 1.2-.51.59-.96 1.54-.84 2.45.89.07 1.8-.45 2.35-1.12z" fill="#050505" />
    </svg>
  );
}

/**
 * Google and Apple sign-in. The backend has no OAuth provider yet, so the
 * buttons are shown disabled rather than hidden, to keep the layout.
 */
export function SocialButtons() {
  return (
    <>
      <div className={styles.socials}>
        <button type="button" className={styles.social} disabled title="Coming soon">
          <GoogleIcon />
          Google
        </button>
        <button type="button" className={styles.social} disabled title="Coming soon">
          <AppleIcon />
          Apple
        </button>
      </div>
      <div className={styles.divider}>
        <span className={styles.dividerLine} />
        or with phone
        <span className={`${styles.dividerLine} ${styles.dividerLineR}`} />
      </div>
    </>
  );
}

export function AuthSwitch({ children }: { children: ReactNode }) {
  return <p className={styles.switch}>{children}</p>;
}

export { styles as authStyles };
