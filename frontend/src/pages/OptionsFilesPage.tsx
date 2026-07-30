import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { apiRequest } from "../api";
import type { LicenseDaemon, LicenseServer, OptionsFile } from "../types";

export function OptionsFilesPage() {
  const [servers, setServers] = useState<LicenseServer[]>([]);
  const [daemons, setDaemons] = useState<LicenseDaemon[]>([]);
  const [optionsFiles, setOptionsFiles] = useState<OptionsFile[]>([]);

  const [selectedServerId, setSelectedServerId] = useState<string>("");
  const [selectedDaemonId, setSelectedDaemonId] = useState<string>("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function loadServers() {
    const response = await apiRequest<LicenseServer[]>("/license-servers");
    setServers(response);

    if (!selectedServerId && response.length > 0) {
      setSelectedServerId(String(response[0].id));
    }
  }

  async function loadOptions(serverId: string) {
    if (!serverId) return;

    const response = await apiRequest<OptionsFile[]>(
      `/license-servers/${serverId}/options-files`
    );

    setOptionsFiles(response);
  }

  async function loadDaemons(serverId: string) {
    if (!serverId) return;

    const response = await apiRequest<LicenseDaemon[]>(
      `/license-servers/${serverId}/daemons`
    );

    setDaemons(response);
    setSelectedDaemonId(response.length > 0 ? String(response[0].id) : "");
  }

  useEffect(() => {
    loadServers().catch((err) =>
      setError(err instanceof Error ? err.message : "Failed to load servers")
    );
  }, []);

  useEffect(() => {
    if (selectedServerId) {
      Promise.all([
        loadOptions(selectedServerId),
        loadDaemons(selectedServerId),
      ]).catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load options configuration"
        )
      );
    }
  }, [selectedServerId]);

  async function createOptions(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      await apiRequest(`/license-servers/${selectedServerId}/options-files`, {
        method: "POST",
        body: JSON.stringify({
          daemon_id: Number(selectedDaemonId),
          content,
        }),
      });

      setContent("");
      await loadOptions(selectedServerId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create options file");
    }
  }

  const selectedDaemon = daemons.find(
    (daemon) => daemon.id === Number(selectedDaemonId)
  );

  async function recordOptions(id: number) {
    setError(null);

    try {
      await apiRequest(`/options-files/${id}/record`, {
        method: "POST",
      });

      await loadOptions(selectedServerId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to record options file");
    }
  }

  return (
    <div className="page-layout">
      <div className="page-header">
        <h1>Options Files</h1>
        <p>Manage FlexLM options files as controlled artifacts.</p>
      </div>

      <div className="two-column-grid">
        <section className="card">
          <h2>Create Options File</h2>

          <form className="form-grid" onSubmit={createOptions}>
            <label>
              Server
              <select
                value={selectedServerId}
                onChange={(event) => setSelectedServerId(event.target.value)}
              >
                {servers.map((server) => (
                  <option key={server.id} value={server.id}>
                    {server.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Vendor Daemon
              <select
                value={selectedDaemonId}
                onChange={(event) => setSelectedDaemonId(event.target.value)}
              >
                {daemons.map((daemon) => (
                  <option key={daemon.id} value={daemon.id}>
                    {daemon.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="configured-path">
              <strong>Configured options path</strong>
              <code>{selectedDaemon?.options_file_path ?? "Not configured"}</code>
            </div>

            <label>
              Content
              <textarea
                rows={12}
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="GROUP weekend_users alice bob
RESERVE 2 VCS GROUP weekend_users"
              />
            </label>

            <button
              type="submit"
              disabled={!selectedDaemonId || !selectedDaemon?.options_file_path}
            >
              Create Options File
            </button>
          </form>

          {error && <div className="error">{error}</div>}
        </section>

        <section className="card">
          <h2>Existing Options Files</h2>

          <div className="server-list">
            {optionsFiles.map((item) => (
              <div className="server-card" key={item.id}>
                <div className="server-card-header">
                  <h3>{item.filename}</h3>
                  <span className="badge">
                    {item.content_backend ?? "not recorded"}
                  </span>
                </div>
                <p>{item.storage_path}</p>
                <p>Updated: {item.updated_at}</p>
                {!item.content_backend && (
                  <button onClick={() => recordOptions(item.id)}>Record</button>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
