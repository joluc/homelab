{{/* Override the redis.url helper to fix port formatting and add auth */}}
{{- define "redis.url" -}}
{{- if eq .Values.redis.external.enabled .Values.redis.internal.enabled -}}
{{- fail "redis.url: redis.external.enabled and redis.internal.enabled are equal" -}}
{{- end -}}
{{- if .Values.redis.external.enabled -}}
{{- printf "redis://:redis-password-change-me@%s:%v" .Values.redis.external.host .Values.redis.external.port -}}
{{- else -}}
{{- printf "redis://%s-redis:6379" .Release.Name -}}
{{- end -}}
{{- end -}}
