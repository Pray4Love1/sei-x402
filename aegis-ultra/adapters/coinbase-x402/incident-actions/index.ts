export type Incident = {
  id: string;
  reason: string;
  severity: "low" | "medium" | "high";
};

export function escalateIncident(incident: Incident): string {
  return `incident:${incident.id}:${incident.severity}`;
}
