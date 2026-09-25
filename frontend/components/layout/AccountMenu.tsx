"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Popover } from "@/components/ui/Popover";
import { logout } from "@/features/auth/api";
import { routes } from "@/lib/constants/routes";
import type { Account } from "@/types/account";

import styles from "./Header.module.css";

/** The signed-in chip: initials, short name and a menu. */

function initials(account: Account): string {
  const letters = `${account.first_name.charAt(0)}${account.last_name.charAt(0)}`.toUpperCase();
  return letters || account.phone_number.slice(-2);
}

function shortName(account: Account): string {
  if (!account.first_name) return "My account";
  return account.last_name ? `${account.first_name} ${account.last_name.charAt(0)}.` : account.first_name;
}

export function AccountMenu({ account }: { account: Account }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);

  const onLogout = async () => {
    setLeaving(true);
    try {
      await logout();
    } finally {
      setOpen(false);
      router.push(routes.home);
      router.refresh();
    }
  };

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
      align="end"
      triggerClassName={styles.account}
      trigger={
        <>
          <span className={styles.avatar} aria-hidden="true">
            {initials(account)}
          </span>
          <span className={styles.accountName}>{shortName(account)}</span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </>
      }
    >
      <ul className={styles.menu}>
        <li>
          <Link href={routes.account.root} className={styles.menuItem} onClick={() => setOpen(false)}>
            My account
          </Link>
        </li>
        <li>
          <Link href={routes.account.listProperty} className={styles.menuItem} onClick={() => setOpen(false)}>
            List a property
          </Link>
        </li>
        <li>
          <button type="button" className={styles.menuItem} onClick={onLogout} disabled={leaving}>
            {leaving ? "Logging out…" : "Log out"}
          </button>
        </li>
      </ul>
    </Popover>
  );
}
