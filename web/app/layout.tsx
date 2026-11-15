import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "OrbitRisk | Satellite Conjunction Risk Modeling", description: "Explore public-TLE orbital trajectories, geometric conjunction screening, and explicitly synthetic uncertainty experiments.", robots: { index: true, follow: true } };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
