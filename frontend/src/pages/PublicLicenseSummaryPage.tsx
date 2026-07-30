import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api";


type LicenseSummaryItem = {
  license_server: string;
  feature: string;
  count: number;
  expiry_date: string | null;
};

type LicenseSummaryResponse = {
  generated_at: string;
  items: LicenseSummaryItem[];
};


function formatExpiry(value: string | null): string {
  if (!value) return "Permanent";

  const parsed = new Date(`${value}T00:00:00Z`);

  if (Number.isNaN(parsed.getTime())) return value;

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}


export function PublicLicenseSummaryPage() {
  const [summary, setSummary] = useState<LicenseSummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<LicenseSummaryResponse>("/public/license-summary")
      .then(setSummary)
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load licence summary"
        )
      );
  }, []);

  return (
    <div className="public-summary-page">
      <header className="public-summary-header">
        <div>
          <span className="eyebrow">FlexLM Portal</span>
          <h1>Licence availability</h1>
          <p>
            Current licence quantities grouped by server, feature and expiry date.
          </p>
        </div>
        <Link className="secondary-link" to="/login">Portal login</Link>
      </header>

      <main className="public-summary-card">
        {error && <div className="error">{error}</div>}

        {!summary && !error && <p>Loading licence summary…</p>}

        {summary && summary.items.length === 0 && (
          <p>No active licence information is available.</p>
        )}

        {summary && summary.items.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Licence Server</th>
                  <th>Feature</th>
                  <th>Count</th>
                  <th>Expiry Date</th>
                </tr>
              </thead>
              <tbody>
                {summary.items.map((item) => (
                  <tr
                    key={[
                      item.license_server,
                      item.feature,
                      item.expiry_date ?? "permanent",
                    ].join("|")}
                  >
                    <td>{item.license_server}</td>
                    <td>{item.feature}</td>
                    <td className="licence-count">{item.count}</td>
                    <td>{formatExpiry(item.expiry_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {summary && (
          <p className="summary-updated">
            Updated{" "}
            {new Intl.DateTimeFormat("en-GB", {
              dateStyle: "medium",
              timeStyle: "short",
              timeZone: "UTC",
            }).format(new Date(summary.generated_at))}{" "}
            UTC
          </p>
        )}
      </main>
    </div>
  );
}
