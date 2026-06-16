export type LicenseServer = {
  id: number;
  name: string;
  hostname: string;
  hostid: string;
  lmgrd_port: number | null;
  merge_policy: string;
};

export type LicenseFile = {
  id: number;
  server_id: number | null;
  filename: string;
  vendor: string | null;
  server_hostname: string | null;
  server_hostid: string | null;
  storage_path: string | null;
  imported_at: string;
  content_backend: string | null;
  content_ref: string | null;
  content_path: string | null;
  feature_count: number;
  published_at: string | null;
  publish_status: string | null;
  publish_message: string | null;
};

export type Deployment = {
  id: number;
  server_id: number;
  artifact_path: string;
  status: string;
  generated_at: string;
  content_backend: string | null;
  content_ref: string | null;
  content_path: string | null;
  published_at: string | null;
  publish_status: string | null;
  publish_message: string | null;
};

export type OptionsFile = {
  id: number;
  server_id: number;
  filename: string;
  content?: string;
  storage_path: string | null;
  content_backend: string | null;
  content_ref: string | null;
  content_path: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  publish_status: string | null;
  publish_message: string | null;
};

export type AuditEvent = {
  id: number;
  actor: string | null;
  action: string;
  object_type: string | null;
  object_id: string | null;
  details: string | null;
  created_at: string;
};

export type LicenseDaemon = {
  id: number;
  server_id: number;
  name: string;
  daemon_path: string | null;
  options_file_path: string | null;
  port: number | null;
  served_vendors: string | null;
};

export type ValidationResult = {
  severity: string;
  code: string;
  message: string;
  created_at: string;
};
