import Link from "next/link";

import { routes } from "@/lib/constants/routes";
import type { Account } from "@/types/account";

import { AccountMenu } from "./AccountMenu";
import styles from "./Header.module.css";
import { NavLinks } from "./NavLinks";

/**
 * The site navigation: one bar fading from the black brand side into gold,
 * with section links and the auth actions on the right.
 */

function UserIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <circle cx="9" cy="6.25" r="3" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M3.5 15.25C4.2 12.6 6.4 11 9 11C11.6 11 13.8 12.6 14.5 15.25"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
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
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Header({ account }: { account: Account | null }) {
  return (
    <header className={styles.header}>
      <span className={styles.lineTop} aria-hidden="true" />
      <span className={styles.lineBottom} aria-hidden="true" />

      <div className={styles.brandPanel}>
        <Link href={routes.home} className={styles.brand}>
          MONUMENT<sup>®</sup>
        </Link>
      </div>

      <div className={styles.navPanel}>
        <nav aria-label="Main">
          <NavLinks />
        </nav>

        <div className={styles.auth}>
          {account ? (
            <AccountMenu account={account} />
          ) : (
            <>
              <Link href={routes.login} className={styles.login} aria-label="Log in">
                <UserIcon />
                <span>Log in</span>
              </Link>
              <span className={styles.signupRing}>
                <Link href={routes.register} className={styles.signup}>
                  <span className={styles.signupLabel}>Sign up</span>
                  <span className={styles.signupIcon}>
                    <ArrowIcon />
                  </span>
                </Link>
              </span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
