import { useState } from "react";
import { apiRequest } from "../api";

export function DashboardPage() {
  const [publishMessage, setPublishMessage] = useState<string | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  async function publishContent() {
    setPublishMessage(null);
    setPublishError(null);

    try {
      const response = await apiRequest<{
        backend: string;
        published: boolean;
        message: string;
        updated: {
          license_files: number;
          deployments: number;
          options_files: number;
        };
      }>("/content/publish", {
        method: "POST",
      });

      setPublishMessage(
        `Published via ${response.backend}. Updated: ` +
          `${response.updated.license_files} uploads, ` +
          `${response.updated.deployments} deployments, ` +
          `${response.updated.options_files} options files.`
      );
    } catch (err) {
      setPublishError(
        err instanceof Error ? err.message : "Publish failed"
      );
    }
  }

  return (
    <section className="card-grid">
      <div className="card">
        <h3>License Servers</h3>
        <p>Manage FlexLM server definitions and merge policies.</p>
      </div>

      <div className="card">
        <h3>License Uploads</h3>
        <p>Upload vendor license artifacts and parse metadata.</p>
      </div>

      <div className="card">
        <h3>Deployments</h3>
        <p>Generate deployment-ready license.dat artifacts.</p>
      </div>

      <div className="card">
        <h3>Options Files</h3>
        <p>Manage vendor options files as controlled artifacts.</p>
      </div>

      <div className="card">
        <h3>Content Publishing</h3>
        <p>Push recorded artifacts to the configured remote backend.</p>
        <button onClick={publishContent}>Publish Content</button>
        {publishMessage && <p className="success-text">{publishMessage}</p>}
        {publishError && <div className="error">{publishError}</div>}
      </div>
    </section>
  );
}
