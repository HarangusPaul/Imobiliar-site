"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import {
  Checkbox,
  Field,
  FormAlert,
  GoldButton,
  PasswordInput,
  PhoneInput,
  TextInput,
  toE164,
} from "@/components/ui/form/controls";
import { routes } from "@/lib/constants/routes";
import { emptyFormState, firstError, formStateFromError, type FormState } from "@/lib/validation/form";

import { login, register } from "../api";
import { registerSchema } from "../schema";

import { authStyles as styles, AuthSwitch } from "./AuthShell";

/**
 * Account creation. The backend creates the account without opening a
 * session, so a successful registration is followed by a login. The
 * "I'm looking to" choice is not stored; it decides where the new member lands.
 */

const INTENTS: Array<{ value: string; label: string; href: Route }> = [
  { value: "buy", label: "Buy", href: routes.buy },
  { value: "rent", label: "Rent", href: routes.rent },
  { value: "stay", label: "Stay", href: routes.stay },
];

function passwordStrength(value: string): { score: number; label: string } {
  if (!value) return { score: 0, label: "" };
  let score = 0;
  if (value.length >= 8) score++;
  if (value.length >= 12) score++;
  if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score++;
  if (/\d/.test(value)) score++;
  if (/[^A-Za-z0-9]/.test(value)) score++;
  const label = value.length < 8 ? "Too short" : ["Weak", "Weak", "Fair", "Good", "Strong", "Strong"][score]!;
  return { score: value.length < 8 ? 1 : score, label };
}

export function RegisterForm() {
  const router = useRouter();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [country, setCountry] = useState("RO");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [intent, setIntent] = useState("buy");
  const [terms, setTerms] = useState(false);
  const [state, setState] = useState<FormState>(emptyFormState);
  const [pending, setPending] = useState(false);

  const strength = passwordStrength(password);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = {
      first_name: firstName,
      last_name: lastName,
      phone_number: phone ? toE164(country, phone) : "",
      password,
    };
    const parsed = registerSchema.safeParse(values);
    const fieldErrors: Record<string, string[]> = parsed.success
      ? {}
      : { ...parsed.error.flatten().fieldErrors };
    if (!terms) fieldErrors.terms = ["Please accept the terms to continue."];
    if (!parsed.success || !terms) {
      setState({ fieldErrors, formError: "" });
      return;
    }

    setPending(true);
    setState(emptyFormState);
    try {
      await register(parsed.data);
    } catch (error) {
      setState(formStateFromError(error));
      setPending(false);
      return;
    }

    try {
      await login({ phone_number: parsed.data.phone_number, password, remember: true });
      router.replace(INTENTS.find((i) => i.value === intent)?.href ?? routes.home);
      router.refresh();
    } catch {
      // The account exists; let them sign in by hand.
      router.replace(routes.login);
    }
  };

  return (
    <form className={styles.form} onSubmit={onSubmit} noValidate>
      <FormAlert>{state.formError}</FormAlert>

      <div className={styles.fields}>
        <div className={styles.two}>
          <Field label="First name" htmlFor="reg-first" error={firstError(state, "first_name")}>
            <TextInput
              id="reg-first"
              name="first_name"
              autoComplete="given-name"
              placeholder="First name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              autoFocus
            />
          </Field>
          <Field label="Last name" htmlFor="reg-last" error={firstError(state, "last_name")}>
            <TextInput
              id="reg-last"
              name="last_name"
              autoComplete="family-name"
              placeholder="Last name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </Field>
        </div>

        <Field
          label="Phone number"
          htmlFor="reg-phone"
          error={firstError(state, "phone_number")}
          hint="You’ll use this number to log in."
        >
          <PhoneInput
            id="reg-phone"
            name="phone"
            country={country}
            onCountryChange={setCountry}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="721 234 567"
            invalid={Boolean(firstError(state, "phone_number"))}
          />
        </Field>

        <Field label="Password" htmlFor="reg-password" error={firstError(state, "password")}>
          <PasswordInput
            id="reg-password"
            name="password"
            autoComplete="new-password"
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            invalid={Boolean(firstError(state, "password"))}
          />
          {password ? (
            <div className={styles.strength} aria-live="polite">
              <span className={styles.strengthTrack}>
                <span className={styles.strengthFill} style={{ width: `${(strength.score / 5) * 100}%` }} />
              </span>
              <span className={styles.strengthText}>{strength.label}</span>
            </div>
          ) : null}
        </Field>

        <Field label="I’m looking to" asGroup>
          <div className={styles.chips}>
            {INTENTS.map((option) => {
              const on = intent === option.value;
              return (
                <label key={option.value} className={`${styles.chip} ${on ? styles.chipOn : ""}`}>
                  <input
                    type="radio"
                    name="intent"
                    value={option.value}
                    className="visually-hidden"
                    checked={on}
                    onChange={() => setIntent(option.value)}
                  />
                  {on ? <span className={styles.dot} aria-hidden="true" /> : null}
                  {option.label}
                </label>
              );
            })}
          </div>
        </Field>
      </div>

      <Field label={<span className="visually-hidden">Terms</span>} error={firstError(state, "terms")}>
        <Checkbox checked={terms} onChange={setTerms} invalid={Boolean(firstError(state, "terms"))}>
          <span className={styles.terms}>
            I agree to the <Link href={routes.about}>Terms</Link> and{" "}
            <Link href={routes.about}>Privacy policy</Link>
          </span>
        </Checkbox>
      </Field>

      <GoldButton block loading={pending}>
        Create account
      </GoldButton>

      <AuthSwitch>
        Already a member? <Link href={routes.login}>Log in</Link>
      </AuthSwitch>
    </form>
  );
}
