import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { apiRequest } from "../api";
import type { LicenseDaemon, LicenseServer } from "../types";

export function LicenseServersPage() {
  const [servers, setServers] = useState<LicenseServer[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [hostname, setHostname] = useState("");
  const [hostid, setHostid] = useState("");

  const [lmgrdPort, setLmgrdPort] = useState("27000");
  const [mergePolicy, setMergePolicy] = useState("additive");

  const [daemonsByServer, setDaemonsByServer] = useState<
    Record<number, LicenseDaemon[]>
  >({});

  const [daemonForms, setDaemonForms] = useState<
    Record<number, {
      name: string;
      daemon_path: string;
      options_file_path: string;
      port: string;
      served_vendors: string;
    }>
  >({});

  async function deleteDaemon(serverId: number, daemonId: number) {
    setError(null);

    try {
      await apiRequest(`/license-daemons/${daemonId}`, {
        method: "DELETE",
      });

      await loadDaemons(serverId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete daemon");
    }
  }

  async function loadDaemons(serverId: number) {
    const response = await apiRequest<LicenseDaemon[]>(
      `/license-servers/${serverId}/daemons`
    );

    setDaemonsByServer((current) => ({
      ...current,
      [serverId]: response,
    }));
  }

  async function loadAllDaemons(serverList: LicenseServer[]) {
    await Promise.all(
      serverList.map((server) => loadDaemons(server.id))
    );
  }

  function updateDaemonForm(
    serverId: number,
    field: "name" | "daemon_path" | "options_file_path" | "port" | "served_vendors",
    value: string
  ) {
    setDaemonForms((current) => ({
      ...current,
      [serverId]: {
        name: current[serverId]?.name ?? "",
        daemon_path: current[serverId]?.daemon_path ?? "",
        options_file_path: current[serverId]?.options_file_path ?? "",
        port: current[serverId]?.port ?? "",
        served_vendors: current[serverId]?.served_vendors ?? "",
        [field]: value,
      },
    }));
  }

  async function createDaemon(serverId: number) {
    const form = daemonForms[serverId];
  
    if (!form?.name) {
      setError("Daemon name is required");
      return;
    }

    await apiRequest(`/license-servers/${serverId}/daemons`, {
      method: "POST",
      body: JSON.stringify({
        name: form.name,
        daemon_path: form.daemon_path || null,
        options_file_path: form.options_file_path || null,
        port: form.port ? Number(form.port) : null,
        served_vendors: form.served_vendors ? Number(form.served_vendors) : null,
      }),
    });

    setDaemonForms((current) => ({
      ...current,
      [serverId]: {
        name: "",
        daemon_path: "",
        options_file_path: "",
        port: "",
        served_vendors: "",
      },
    }));

    await loadDaemons(serverId);
  }

  async function loadServers() {
    setLoading(true);
    setError(null);

    try {
      const response = await apiRequest<LicenseServer[]>(
        "/license-servers"
      );

      setServers(response);
      await loadAllDaemons(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load servers");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadServers();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      await apiRequest("/license-servers", {
        method: "POST",
        body: JSON.stringify({
          name,
          hostname,
          hostid,
          lmgrd_port: Number(lmgrdPort),
          merge_policy: mergePolicy,
        }),
      });

      setName("");
      setHostname("");
      setHostid("");
      setLmgrdPort("27000");

      await loadServers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create server");
    }
  }

  return (
    <div className="page-layout">
      <div className="page-header">
        <div>
          <h1>License Servers</h1>
          <p>Manage FlexLM server definitions and merge policies.</p>
        </div>
      </div>

      <div className="two-column-grid">
        <section className="card">
          <h2>Create License Server</h2>

          <form className="form-grid" onSubmit={handleSubmit}>
            <label>
              Name
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </label>

            <label>
              Hostname
              <input
                value={hostname}
                onChange={(e) => setHostname(e.target.value)}
                required
              />
            </label>

            <label>
              HostID
              <input
                value={hostid}
                onChange={(e) => setHostid(e.target.value)}
                required
              />
            </label>

            <label>
              lmgrd Port
              <input
                value={lmgrdPort}
                onChange={(e) => setLmgrdPort(e.target.value)}
              />
            </label>

            <label>
              Merge Policy
              <select
                value={mergePolicy}
                onChange={(e) => setMergePolicy(e.target.value)}
              >
                <option value="additive">additive</option>
                <option value="latest_only">latest_only</option>
              </select>
            </label>

            <button type="submit">Create Server</button>
          </form>

          {error && <div className="error">{error}</div>}
        </section>

        <section className="card">
          <h2>Configured Servers</h2>

          {loading ? (
            <p>Loading...</p>
          ) : servers.length === 0 ? (
            <p>No license servers configured.</p>
          ) : (
            <div className="server-list">
              {servers.map((server) => (
                <div className="server-card" key={server.id}>
                  <div className="server-card-header">
                    <h3>{server.name}</h3>
                    <span className="badge">{server.merge_policy}</span>
                  </div>

                  <div className="server-grid">
                    <div>
                      <strong>Hostname</strong>
                      <div>{server.hostname}</div>
                    </div>

                    <div>
                      <strong>HostID</strong>
                      <div>{server.hostid}</div>
                    </div>

                    <div>
                      <strong>lmgrd Port</strong>
                      <div>{server.lmgrd_port ?? "-"}</div>
                    </div>

                    <div className="daemon-section">
                      <h4>Vendor Daemons</h4>

                      {(daemonsByServer[server.id] ?? []).length === 0 ? (
                        <p>No daemons configured.</p>
                      ) : (
                        <div className="daemon-list">
                          {(daemonsByServer[server.id] ?? []).map((daemon) => (
                            <div className="daemon-row" key={daemon.id}>
                              <div className="daemon-topline">
                                <strong>{daemon.name}</strong>
                                <span>port={daemon.port ?? "-"}</span>
                                <button
                                  type="button"
                                  onClick={() => deleteDaemon(server.id, daemon.id)}
                                >
                                  Delete
                                </button>
                              </div>
                              <div className="daemon-detail">
                                <strong>Daemon:</strong> {daemon.daemon_path ?? "-"}
                              </div>
                              <div className="daemon-detail">
                                <strong>Options:</strong> {daemon.options_file_path ?? "-"}
                              </div>
                              <div className="daemon-detail">
                                <strong>Served Vendors:</strong> {daemon.served_vendors ?? "-"}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="daemon-form">
                        <input
                          placeholder="daemon name"
                          value={daemonForms[server.id]?.name ?? ""}
                          onChange={(e) =>
                            updateDaemonForm(server.id, "name", e.target.value)
                          }
                        />

                        <input
                          placeholder="daemon path"
                          value={daemonForms[server.id]?.daemon_path ?? ""}
                          onChange={(e) =>
                            updateDaemonForm(server.id, "daemon_path", e.target.value)
                          }
                        />

                        <input
                          placeholder="port"
                          value={daemonForms[server.id]?.port ?? ""}
                          onChange={(e) =>
                            updateDaemonForm(server.id, "port", e.target.value)
                          }
                        />

                        <input
                          placeholder="options file path"
                          value={daemonForms[server.id]?.options_file_path ?? ""}
                          onChange={(e) =>
                            updateDaemonForm(server.id, "options_file_path", e.target.value)
                          }
                        />

                        <input
                          placeholder="served vendors"
                          value={daemonForms[server.id]?.served_vendors ?? ""}
                          onChange={(e) =>
                            updateDaemonForm(server.id, "served_vendors", e.target.value)
                          }
                        />

                        <button type="button" onClick={() => createDaemon(server.id)}>
                          Add Daemon
                        </button>
                      </div>
                    </div>

                  </div>

                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
