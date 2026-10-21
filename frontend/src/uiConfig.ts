export async function loadUxVersion(apiBaseUrl: string): Promise<1 | 2> {
  const response = await fetch(`${apiBaseUrl}/ui-config`, {
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
  // An older backend can still serve the original interface during upgrades.
  if (response.status === 404) return 1;
  if (!response.ok) throw new Error("Unable to load portal configuration.");
  const config = await response.json();
  if (config?.ux_version !== 1 && config?.ux_version !== 2) {
    throw new Error("Invalid portal interface configuration.");
  }
  return config.ux_version;
}
