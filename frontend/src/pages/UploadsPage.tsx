import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { apiRequest } from "../api";
import type { LicenseFile } from "../types";

type ImportResponse = {
  license_file_id: number;
  matched_server: {
    id: number;
    name: string;
    hostname: string;
    hostid: string;
  } | null;
  parsed: {
    server: {
      hostname: string;
      hostid: string;
    } | null;
    vendor: string | null;
    features: Array<{
      name: string;
      vendor: string;
      version: string;
      expiry: string;
      count: number | string;
    }>;
  };
  storage_path: string;
};

export function UploadsPage() {
  const [files, setFiles] = useState<LicenseFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [lastImport, setLastImport] = useState<ImportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function deleteUpload(id: number) {
    if (!confirm(`Delete upload ${id}?`)) return;

    await apiRequest(`/license-files/${id}`, {
      method: "DELETE",
    });

    await loadFiles();
  }

  async function loadFiles() {
    try {
      const response = await apiRequest<LicenseFile[]>("/license-files");
      setFiles(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load uploads");
    }
  }

  useEffect(() => {
    loadFiles();
  }, []);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Choose a license file first");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await apiRequest<ImportResponse>("/license-files/import", {
        method: "POST",
        body: formData,
      });

      setLastImport(response);
      setSelectedFile(null);
      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function recordUpload(id: number) {
    setError(null);

    try {
      await apiRequest(`/license-files/${id}/record`, {
        method: "POST",
      });

      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to record upload");
    }
  }

  return (
    <div className="page-layout">
      <div className="page-header">
        <h1>Uploads</h1>
        <p>Upload vendor license files, parse metadata, and record artifacts.</p>
      </div>

      <div className="two-column-grid">
        <section className="card">
          <h2>Import License File</h2>

          <form className="form-grid" onSubmit={handleUpload}>
            <label>
              License file
              <input
                type="file"
                onChange={(event) =>
                  setSelectedFile(event.target.files?.[0] ?? null)
                }
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Uploading..." : "Upload and Parse"}
            </button>
          </form>

          {error && <div className="error">{error}</div>}

          {lastImport && (
            <div className="result-box">
              <h3>Last Import</h3>
              <p>
                <strong>ID:</strong> {lastImport.license_file_id}
              </p>
              <p>
                <strong>Matched server:</strong>{" "}
                {lastImport.matched_server
                  ? lastImport.matched_server.name
                  : "No match"}
              </p>
              <p>
                <strong>Vendor:</strong> {lastImport.parsed.vendor ?? "-"}
              </p>
              <p>
                <strong>Features:</strong> {lastImport.parsed.features.length}
              </p>
            </div>
          )}
        </section>

        <section className="card">
          <h2>Recent Uploads</h2>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Filename</th>
                  <th>Vendor</th>
                  <th>HostID</th>
                  <th>Features</th>
                  <th>Content</th>
                  <th></th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr key={file.id}>
                    <td>{file.id}</td>
                    <td>{file.filename}</td>
                    <td>{file.vendor ?? "-"}</td>
                    <td>{file.server_hostid ?? "-"}</td>
                    <td>{file.feature_count}</td>
                    <td>{file.content_backend ?? "not recorded"}</td>
                    <td>
                      {file.content_backend ? (
                        <span className="status-pill status-recorded">recorded</span>
                      ) : (
                        <span className="status-pill status-warning">not recorded</span>
                      )}
                    </td>
                    <td><div className="action-buttons"><button onClick={() => deleteUpload(file.id)}> Delete </button></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
