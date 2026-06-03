import { useEffect, useState } from "react";
import { apiRequest, apiTextRequest } from "../api";
import type { Deployment, LicenseServer, ValidationResult } from "../types";

export function DeploymentsPage() {
  const [artifactText, setArtifactText] = useState<string | null>(null);
  const [artifactTitle, setArtifactTitle] = useState<string | null>(null);
  const [servers, setServers] = useState<LicenseServer[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [selectedServerId, setSelectedServerId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [validationByDeployment, setValidationByDeployment] = useState<Record<number, ValidationResult[]> >({});

  async function loadData() {
    try {
      const [serverResponse, deploymentResponse] = await Promise.all([
        apiRequest<LicenseServer[]>("/license-servers"),
        apiRequest<Deployment[]>("/deployments"),
      ]);

      setServers(serverResponse);
      setDeployments(deploymentResponse);

      await Promise.all(
        deploymentResponse.map((deployment) =>
          loadValidation(deployment.id)
        )
      );

      if (!selectedServerId && serverResponse.length > 0) {
        setSelectedServerId(String(serverResponse[0].id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load deployments");
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function loadValidation(deploymentId: number) {
    const response = await apiRequest<ValidationResult[]>(
      `/deployments/${deploymentId}/validation`
    );

    setValidationByDeployment((current) => ({
      ...current,
      [deploymentId]: response,
    }));
  }

  async function generateDeployment() {
    if (!selectedServerId) return;

    setError(null);

    try {
      await apiRequest(`/license-servers/${selectedServerId}/generate-deployment`, {
        method: "POST",
      });

      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate deployment");
    }
  }

  async function recordDeployment(id: number) {
    setError(null);

    try {
      await apiRequest(`/deployments/${id}/record`, {
        method: "POST",
      });

      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to record deployment");
    }
  }

  async function viewDeployment(deployment: Deployment) {
    setError(null);

    try {
      const text = await apiTextRequest(
        `/deployments/${deployment.id}/artifact`
      );

      setArtifactTitle(`Deployment ${deployment.id} — license.dat`);
      setArtifactText(text);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load deployment artifact"
      );
    }
  }

  return (
    <div className="page-layout">
      <div className="page-header">
        <h1>Deployments</h1>
        <p>Generate and record deployment-ready license artifacts.</p>
      </div>

      <section className="card">
        <h2>Generate Deployment</h2>

        <div className="inline-form">
          <select
            value={selectedServerId}
            onChange={(event) => setSelectedServerId(event.target.value)}
          >
            {servers.map((server) => (
              <option key={server.id} value={server.id}>
                {server.name} ({server.merge_policy})
              </option>
            ))}
          </select>

          <button onClick={generateDeployment}>Generate</button>
        </div>

        {error && <div className="error">{error}</div>}
      </section>

      <section className="card">
        <h2>Deployment History</h2>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Server</th>
                <th>Status</th>
                <th>Artifact</th>
                <th>Content</th>
                <th>Generated</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {deployments.map((deployment) => (
                <>
                  <tr key={deployment.id}>
                    <td>{deployment.id}</td>
                    <td>{deployment.server_id}</td>
                    <td>
                      <span className={`status-pill status-${deployment.status}`}>
                        {deployment.status}
                      </span>
                    </td>
                    <td>{deployment.artifact_path}</td>
                    <td>
                      {deployment.content_backend ? (
                        <span className="status-pill status-recorded">recorded</span>
                      ) : (
                        <span className="status-pill status-warning">not recorded</span>
                      )}
                    </td>
                    <td>{deployment.generated_at}</td>
                    <td>
                      <div className="action-buttons">
                        <button onClick={() => viewDeployment(deployment)}>
                          View
                        </button>
                      </div>
                    </td>
                  </tr>
                  {(validationByDeployment[deployment.id] ?? []).length > 0 && (
                    <tr>
                      <td colSpan={7}>
                        <div className="validation-list">
                          {(validationByDeployment[deployment.id] ?? []).map(
                            (item, index) => (
                              <div
                                className={`validation-item validation-${item.severity}`}
                                key={index}
                              >
                                <strong>{item.severity.toUpperCase()}</strong>
                                <span>{item.message}</span>
                              </div>
                            )
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {artifactText !== null && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal-header">
              <h2>{artifactTitle}</h2>
              <button onClick={() => setArtifactText(null)}>
                Close
              </button>
            </div>
            <pre className="artifact-preview">{artifactText}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
