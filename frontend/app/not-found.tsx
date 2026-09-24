import Link from "next/link";

import { routes } from "@/lib/constants/routes";

export default function NotFound() {
  return (
    <main>
      <h1>Page not found</h1>
      <p>The page you are looking for does not exist or is no longer published.</p>
      <Link href={routes.properties}>Browse properties</Link>
    </main>
  );
}
