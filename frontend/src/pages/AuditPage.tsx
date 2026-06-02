import { useEffect, useState } from "react";
import { apiRequest } from "../api";
import type { AuditEvent } from "../types";

export function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadEvents() {
    try {
      const response = await apiRequest<AuditEvent[]>("/audit-events");
      setEvents(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit events");
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  return (
    <div className="page-layout">
      <div className="page-header">
        <h1>Audit Events</h1>
        <p>Recent recorded administrative and manager actions.</p>
      </div>

      {error && <div className="error">{error}</div>}

      <section className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Object</th>
                <th>Details</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>{event.id}</td>
                  <td>{event.actor ?? "-"}</td>
                  <td>{event.action}</td>
                  <td>
                    {event.object_type ?? "-"}:{event.object_id ?? "-"}
                  </td>
                  <td>
                    <code>{event.details ?? ""}</code>
                  </td>
                  <td>{event.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
