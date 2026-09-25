import styles from "./ContactDetails.module.css";

/** Direct lines to the offices, beside the contact form. */

const OFFICES = [
  { city: "London", phone: "+44 20 7946 0821", hours: "Mon to Fri, 9:00 to 18:00 GMT" },
  { city: "New York", phone: "+1 212 555 0186", hours: "Mon to Fri, 9:00 to 18:00 EST" },
];

const EMAIL = "hello@monument.estate";

export function ContactDetails() {
  return (
    <aside className={styles.info} aria-label="Contact details">
      <div className={styles.card}>
        <span className={styles.glow} aria-hidden="true" />
        <h2 className={styles.title}>Talk to an advisor directly</h2>

        {OFFICES.map((office) => (
          <div key={office.city} className={styles.office}>
            <p className={styles.city}>{office.city}</p>
            <a href={`tel:${office.phone.replace(/\s/g, "")}`} className={styles.phone}>
              {office.phone}
            </a>
            <p className={styles.line}>{office.hours}</p>
          </div>
        ))}

        <a href={`mailto:${EMAIL}`} className={styles.mail}>
          <span className={styles.mailIcon} aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="5" width="18" height="14" rx="2.5" />
              <path d="M4 7l8 6 8-6" />
            </svg>
          </span>
          <span className={styles.mailText}>
            <span className={styles.mailLabel}>General enquiries</span>
            <span className={styles.mailAddr}>{EMAIL}</span>
          </span>
        </a>
      </div>

      <div className={styles.hours}>
        <span className={styles.hoursDot} aria-hidden="true" />
        <div>
          <p className={styles.hoursTitle}>Replies within one working day</p>
          <p className={styles.hoursText}>
            Urgent viewing? Call the office nearest you and we will pick it up the same day.
          </p>
        </div>
      </div>
    </aside>
  );
}
