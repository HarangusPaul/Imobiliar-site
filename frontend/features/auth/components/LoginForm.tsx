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
  toE164,
} from "@/components/ui/form/controls";
import { routes } from "@/lib/constants/routes";
import { emptyFormState, firstError, formStateFromError, type FormState } from "@/lib/validation/form";

import { login } from "../api";
import { loginSchema } from "../schema";

import { authStyles as styles, AuthSwitch } from "./AuthShell";

/** Phone number and password. On success, go to `next` (or home) and refresh the header. */
export function LoginForm({ next }: { next: Route }) {
  const router = useRouter();
  const [country, setCountry] = useState("RO");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [state, setState] = useState<FormState>(emptyFormState);
  const [pending, setPending] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = { phone_number: phone ? toE164(country, phone) : "", password };
    const parsed = loginSchema.safeParse(values);
    if (!parsed.success) {
      setState({ fieldErrors: parsed.error.flatten().fieldErrors, formError: "" });
      return;
    }

    setPending(true);
    setState(emptyFormState);
    try {
      await login({ ...parsed.data, remember });
      router.replace(next);
      router.refresh();
    } catch (error) {
      setState(formStateFromError(error));
      setPending(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={onSubmit} noValidate>
      <FormAlert>{state.formError}</FormAlert>

      <div className={styles.fields}>
        <Field label="Phone number" htmlFor="login-phone" error={firstError(state, "phone_number")}>
          <PhoneInput
            id="login-phone"
            name="phone"
            country={country}
            onCountryChange={setCountry}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="721 234 567"
            invalid={Boolean(firstError(state, "phone_number"))}
            autoFocus
          />
        </Field>

        <Field
          label="Password"
          htmlFor="login-password"
          error={firstError(state, "password")}
          aside={
            <Link href={routes.contact} className={styles.forgot}>
              Forgot password?
            </Link>
          }
        >
          <PasswordInput
            id="login-password"
            name="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            invalid={Boolean(firstError(state, "password"))}
          />
        </Field>
      </div>

      <Checkbox checked={remember} onChange={setRemember} name="remember">
        Keep me logged in
      </Checkbox>

      <GoldButton block loading={pending}>
        Log in
      </GoldButton>

      <AuthSwitch>
        New to Monument? <Link href={routes.register}>Create an account</Link>
      </AuthSwitch>
    </form>
  );
}
