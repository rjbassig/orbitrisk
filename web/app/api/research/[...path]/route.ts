import { NextRequest } from "next/server";
import { readFile } from "node:fs/promises";
import path from "node:path";
const base = () => process.env.ORBITRISK_API_BASE_URL || "http://localhost:8000";
async function snapshot(pathname: string, search: URLSearchParams) {
  const data = JSON.parse(await readFile(path.join(process.cwd(), "public/research/orbitrisk-snapshot.json"), "utf8"));
  if (pathname === "catalog") return data.catalog;
  if (pathname === "provenance") return { source: data.source, snapshot_file: "celestrak-stations.tle", sha256: data.sha256, retrieved_at: data.retrieved_at, objects: data.catalog.length, frame: data.frame, units: data.units, limitation: data.limitation };
  if (pathname.startsWith("trajectory/")) {
    const id = Number(pathname.split("/")[1]);
    const match = data.trajectories.find((item: { object: { norad_id: number } }) => item.object.norad_id === id);
    return match || { detail: "NORAD object is not in the precomputed snapshot" };
  }
  if (pathname === "conjunctions") return { mode: data.mode, generated_at: data.generated_at, ...data.screen, limitations: data.limitation };
  if (pathname === "synthetic/probability") return data.synthetic;
  if (pathname === "synthetic/convergence") return [];
  return { detail: "Snapshot route not found" };
}
export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const pathname = path.join("/");
  if (!process.env.ORBITRISK_API_BASE_URL) return Response.json(await snapshot(pathname, request.nextUrl.searchParams));
  const upstream = new URL(`/api/${path.join("/")}`, base());
  request.nextUrl.searchParams.forEach((value, key) => upstream.searchParams.set(key, value));
  const response = await fetch(upstream, { next: { revalidate: 60 } });
  return new Response(response.body, { status: response.status, headers: { "Content-Type": response.headers.get("Content-Type") || "application/json" } });
}
