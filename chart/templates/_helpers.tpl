{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "chart.prefix" -}}
{{- if ne .Release.Name .Chart.Name }}
{{- .Release.Name | replace .Chart.Name "" | trunc 63 | trimPrefix "-" }}-
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chart.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chart.selectorLabels" -}}
{{ include "chart.labels" . }}
app.kubernetes.io/name: {{ include "chart.name" . }}
app.kubernetes.io/component:
{{- end }}

{{/*
Docker image
*/}}
{{- define "chart.image" -}}
{{- .Values.image.repository }}:{{ .Values.image.tag }}
{{- end }}
