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
app.kubernetes.io/name: {{ .Release.Name }}
app.kubernetes.io/component:
{{- end }}

{{/*
Default pod annotations
*/}}
{{- define "chart.podAnnotations" -}}
k8s.grafana.com/scrape: "true"
k8s.grafana.com/metrics.path: "/-/metrics"
{{- end }}

{{/*
Docker image and pod resources
*/}}
{{- define "chart.imageAndResources" -}}
{{- $image := .ctx.image | default .root.image -}}
image: "{{ $image.repository }}:{{ $image.tag }}"
imagePullPolicy: {{ $image.pullPolicy }}
resources:
{{- toYaml (.ctx.resources | default .root.resources) | nindent 2 }}
{{- end }}
