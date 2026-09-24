import { apiPost, type RequestOptions } from "@/lib/api";
import type { Account } from "@/types/account";

export interface RegisterInput {
  phone_number: string;
  password: string;
  first_name?: string;
  last_name?: string;
  email?: string;
}

export interface LoginInput {
  phone_number: string;
  password: string;
}

export function register(input: RegisterInput): Promise<Account> {
  return apiPost<Account>("/client/auth/register/", input);
}

export function login(input: LoginInput): Promise<Account> {
  return apiPost<Account>("/client/auth/login/", input);
}

export function logout(options?: RequestOptions): Promise<void> {
  return apiPost<void>("/client/auth/logout/", undefined, options);
}
