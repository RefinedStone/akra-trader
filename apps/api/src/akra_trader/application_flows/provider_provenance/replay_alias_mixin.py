from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from datetime import timedelta
import hashlib
import json
from typing import Any
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403


class ReplayIntentAliasMixin:
  @staticmethod
  def _normalize_replay_intent_alias_redaction_policy(value: str | None) -> str:
    if value in {"full", "omit_preview", "summary_only"}:
      return value
    return "full"

  @staticmethod
  def _normalize_replay_intent_alias_retention_policy(value: str | None) -> str:
    if value in {"1d", "7d", "30d", "manual"}:
      return value
    return "30d"

  @staticmethod
  def _build_replay_intent_alias_token(alias_id: str, signature: str | None) -> str:
    return f"{alias_id}.{signature}" if signature else alias_id

  @staticmethod
  def _parse_replay_intent_alias_token(alias_token: str) -> tuple[str, str | None]:
    normalized_token = alias_token.strip()
    if not normalized_token:
      raise ValueError("Replay link alias token is required.")
    separator_index = normalized_token.rfind(".")
    if separator_index <= 0:
      return normalized_token, None
    return (
      normalized_token[:separator_index],
      normalized_token[separator_index + 1:] or None,
    )

  @staticmethod
  def _get_replay_intent_alias_retention_delta(retention_policy: str) -> timedelta | None:
    if retention_policy == "1d":
      return timedelta(days=1)
    if retention_policy == "7d":
      return timedelta(days=7)
    if retention_policy == "30d":
      return timedelta(days=30)
    return None

  def _build_replay_intent_alias_expiry(
    self,
    *,
    retention_policy: str,
    created_at: datetime,
  ) -> datetime | None:
    retention_delta = self._get_replay_intent_alias_retention_delta(retention_policy)
    if retention_delta is None:
      return None
    return created_at + retention_delta

  def _build_replay_intent_alias_audit_expiry(
    self,
    *,
    retention_policy: str,
    recorded_at: datetime,
  ) -> datetime | None:
    retention_delta = self._get_replay_intent_alias_retention_delta(retention_policy)
    if retention_delta is None:
      return None
    return recorded_at + retention_delta

  def _build_replay_intent_alias_signature(
    self,
    *,
    alias_id: str,
    created_at: datetime,
    expires_at: datetime | None,
    intent: dict[str, Any],
    redaction_policy: str,
    template_key: str,
  ) -> str:
    payload = json.dumps(
      {
        "a": alias_id,
        "c": created_at.isoformat(),
        "e": expires_at.isoformat() if expires_at is not None else None,
        "i": intent,
        "r": redaction_policy,
        "t": template_key,
      },
      default=str,
      separators=(",", ":"),
      sort_keys=True,
    )
    digest = hashlib.sha256(
      f"{self._replay_intent_alias_signing_secret}:{payload}".encode("utf-8")
    ).hexdigest()
    return digest[:18]

  def _load_or_create_replay_intent_alias_signing_secret(self) -> str:
    load_secret = getattr(self._runs, "load_replay_intent_alias_signing_secret", None)
    save_secret = getattr(self._runs, "save_replay_intent_alias_signing_secret", None)
    if callable(load_secret):
      existing_secret = load_secret()
      if isinstance(existing_secret, str) and existing_secret.strip():
        return existing_secret.strip()
    next_secret = uuid4().hex
    if callable(save_secret):
      persisted_secret = save_secret(next_secret)
      if isinstance(persisted_secret, str) and persisted_secret.strip():
        return persisted_secret.strip()
    return next_secret

  def _save_replay_intent_alias_record(
    self,
    record: ReplayIntentAliasRecord,
  ) -> ReplayIntentAliasRecord:
    save_alias = getattr(self._runs, "save_replay_intent_alias", None)
    if callable(save_alias):
      return save_alias(record)
    self._replay_intent_alias_records[record.alias_id] = record
    return record

  def _load_replay_intent_alias_record(
    self,
    alias_id: str,
  ) -> ReplayIntentAliasRecord | None:
    get_alias = getattr(self._runs, "get_replay_intent_alias", None)
    if callable(get_alias):
      return get_alias(alias_id)
    return self._replay_intent_alias_records.get(alias_id)

  def _save_replay_intent_alias_audit_record(
    self,
    record: ReplayIntentAliasAuditRecord,
  ) -> ReplayIntentAliasAuditRecord:
    save_audit = getattr(self._runs, "save_replay_intent_alias_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._replay_intent_alias_audit_records[record.audit_id] = record
    return record

  def _list_replay_intent_alias_audit_records(
    self,
    alias_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_replay_intent_alias_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits(alias_id))
    records = [
      record
      for record in self._replay_intent_alias_audit_records.values()
      if alias_id is None or record.alias_id == alias_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _delete_replay_intent_alias_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    delete_audits = getattr(self._runs, "delete_replay_intent_alias_audit_records", None)
    if callable(delete_audits):
      return int(delete_audits(audit_ids))
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._replay_intent_alias_audit_records:
        deleted_count += 1
        del self._replay_intent_alias_audit_records[audit_id]
    return deleted_count

  def _prune_replay_intent_alias_records(self) -> None:
    current_time = self._clock()
    self._replay_intent_alias_records = {
      alias_id: record
      for alias_id, record in self._replay_intent_alias_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }

  def _prune_replay_intent_alias_audit_records(self) -> int:
    current_time = self._clock()
    prune_audits = getattr(self._runs, "prune_replay_intent_alias_audit_records", None)
    if callable(prune_audits):
      return int(prune_audits(current_time))
    original_count = len(self._replay_intent_alias_audit_records)
    self._replay_intent_alias_audit_records = {
      audit_id: record
      for audit_id, record in self._replay_intent_alias_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._replay_intent_alias_audit_records)

  def _record_replay_intent_alias_audit_event(
    self,
    *,
    record: ReplayIntentAliasRecord,
    action: str,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ReplayIntentAliasAuditRecord:
    self._prune_replay_intent_alias_audit_records()
    recorded_at = self._clock()
    audit_record = ReplayIntentAliasAuditRecord(
      audit_id=uuid4().hex[:12],
      alias_id=record.alias_id,
      action=action,
      template_key=record.template_key,
      template_label=record.template_label,
      redaction_policy=record.redaction_policy,
      retention_policy=record.retention_policy,
      recorded_at=recorded_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy=record.retention_policy,
        recorded_at=recorded_at,
      ),
      alias_created_at=record.created_at,
      alias_expires_at=record.expires_at,
      alias_revoked_at=record.revoked_at,
      source_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      detail=(
        "Replay link alias created."
        if action == "created"
        else "Replay link alias revoked."
          if action == "revoked"
          else "Replay link alias resolved."
      ),
    )
    return self._save_replay_intent_alias_audit_record(audit_record)

  def _save_replay_intent_alias_audit_export_artifact_record(
    self,
    record: ReplayIntentAliasAuditExportArtifactRecord,
  ) -> ReplayIntentAliasAuditExportArtifactRecord:
    save_artifact = getattr(self._runs, "save_replay_intent_alias_audit_export_artifact", None)
    if callable(save_artifact):
      return save_artifact(record)
    self._replay_intent_alias_audit_export_artifacts[record.artifact_id] = record
    return record

  def _load_replay_intent_alias_audit_export_artifact_record(
    self,
    artifact_id: str,
  ) -> ReplayIntentAliasAuditExportArtifactRecord | None:
    get_artifact = getattr(self._runs, "get_replay_intent_alias_audit_export_artifact", None)
    if callable(get_artifact):
      return get_artifact(artifact_id)
    return self._replay_intent_alias_audit_export_artifacts.get(artifact_id)

  def _delete_replay_intent_alias_audit_export_artifact_records(self, artifact_ids: tuple[str, ...]) -> int:
    delete_artifacts = getattr(self._runs, "delete_replay_intent_alias_audit_export_artifacts", None)
    if callable(delete_artifacts):
      return int(delete_artifacts(artifact_ids))
    deleted_count = 0
    for artifact_id in artifact_ids:
      if artifact_id in self._replay_intent_alias_audit_export_artifacts:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_artifacts[artifact_id]
    return deleted_count

  def _prune_replay_intent_alias_audit_export_artifact_records(self) -> int:
    current_time = self._clock()
    prune_artifacts = getattr(self._runs, "prune_replay_intent_alias_audit_export_artifacts", None)
    if callable(prune_artifacts):
      return int(prune_artifacts(current_time))
    original_count = len(self._replay_intent_alias_audit_export_artifacts)
    self._replay_intent_alias_audit_export_artifacts = {
      artifact_id: record
      for artifact_id, record in self._replay_intent_alias_audit_export_artifacts.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._replay_intent_alias_audit_export_artifacts)

  def _save_replay_intent_alias_audit_export_job_record(
    self,
    record: ReplayIntentAliasAuditExportJobRecord,
  ) -> ReplayIntentAliasAuditExportJobRecord:
    save_job = getattr(self._runs, "save_replay_intent_alias_audit_export_job", None)
    if callable(save_job):
      return save_job(record)
    self._replay_intent_alias_audit_export_jobs[record.job_id] = record
    return record

  def _load_replay_intent_alias_audit_export_job_record(
    self,
    job_id: str,
  ) -> ReplayIntentAliasAuditExportJobRecord | None:
    get_job = getattr(self._runs, "get_replay_intent_alias_audit_export_job", None)
    if callable(get_job):
      return get_job(job_id)
    return self._replay_intent_alias_audit_export_jobs.get(job_id)

  def _list_replay_intent_alias_audit_export_job_records(
    self,
  ) -> tuple[ReplayIntentAliasAuditExportJobRecord, ...]:
    list_jobs = getattr(self._runs, "list_replay_intent_alias_audit_export_jobs", None)
    if callable(list_jobs):
      return tuple(list_jobs())
    return tuple(
      sorted(
        self._replay_intent_alias_audit_export_jobs.values(),
        key=lambda record: (record.created_at, record.job_id),
        reverse=True,
      )
    )

  def _prune_replay_intent_alias_audit_export_job_records(self) -> int:
    current_time = self._clock()
    prune_jobs = getattr(self._runs, "prune_replay_intent_alias_audit_export_jobs", None)
    if callable(prune_jobs):
      return int(prune_jobs(current_time))
    original_count = len(self._replay_intent_alias_audit_export_jobs)
    self._replay_intent_alias_audit_export_jobs = {
      job_id: record
      for job_id, record in self._replay_intent_alias_audit_export_jobs.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._replay_intent_alias_audit_export_jobs)

  def _delete_replay_intent_alias_audit_export_job_records(self, job_ids: tuple[str, ...]) -> int:
    delete_jobs = getattr(self._runs, "delete_replay_intent_alias_audit_export_jobs", None)
    if callable(delete_jobs):
      return int(delete_jobs(job_ids))
    deleted_count = 0
    for job_id in job_ids:
      if job_id in self._replay_intent_alias_audit_export_jobs:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_jobs[job_id]
    return deleted_count

  def _save_replay_intent_alias_audit_export_job_audit_record(
    self,
    record: ReplayIntentAliasAuditExportJobAuditRecord,
  ) -> ReplayIntentAliasAuditExportJobAuditRecord:
    save_audit = getattr(self._runs, "save_replay_intent_alias_audit_export_job_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._replay_intent_alias_audit_export_job_audit_records[record.audit_id] = record
    return record

  def _list_replay_intent_alias_audit_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditExportJobAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_replay_intent_alias_audit_export_job_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits(job_id))
    records = [
      record
      for record in self._replay_intent_alias_audit_export_job_audit_records.values()
      if job_id is None or record.job_id == job_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _delete_replay_intent_alias_audit_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    delete_audits = getattr(self._runs, "delete_replay_intent_alias_audit_export_job_audit_records", None)
    if callable(delete_audits):
      return int(delete_audits(audit_ids))
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._replay_intent_alias_audit_export_job_audit_records:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_job_audit_records[audit_id]
    return deleted_count

  def _prune_replay_intent_alias_audit_export_job_audit_records(self) -> int:
    current_time = self._clock()
    prune_audits = getattr(self._runs, "prune_replay_intent_alias_audit_export_job_audit_records", None)
    if callable(prune_audits):
      return int(prune_audits(current_time))
    original_count = len(self._replay_intent_alias_audit_export_job_audit_records)
    self._replay_intent_alias_audit_export_job_audit_records = {
      audit_id: record
      for audit_id, record in self._replay_intent_alias_audit_export_job_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._replay_intent_alias_audit_export_job_audit_records)

  def _record_replay_intent_alias_audit_export_job_event(
    self,
    *,
    record: ReplayIntentAliasAuditExportJobRecord,
    action: str,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ReplayIntentAliasAuditExportJobAuditRecord:
    self._prune_replay_intent_alias_audit_export_job_audit_records()
    recorded_at = self._clock()
    audit_record = ReplayIntentAliasAuditExportJobAuditRecord(
      audit_id=uuid4().hex[:12],
      job_id=record.job_id,
      action=action,
      recorded_at=recorded_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=recorded_at,
      ),
      template_key=record.template_key,
      export_format=record.export_format,
      source_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      detail=(
        "Replay alias audit export job created."
        if action == "created"
        else "Replay alias audit export job downloaded."
      ),
    )
    return self._save_replay_intent_alias_audit_export_job_audit_record(audit_record)

  @staticmethod
  def _normalize_replay_intent_alias_audit_action(value: str | None) -> str | None:
    if not isinstance(value, str):
      return None
    normalized = value.strip().lower()
    if normalized in {"created", "resolved", "revoked"}:
      return normalized
    return None

  @classmethod
  def _matches_replay_intent_alias_audit_search(
    cls,
    record: ReplayIntentAliasAuditRecord,
    search: str | None,
  ) -> bool:
    if not isinstance(search, str) or not search.strip():
      return True
    needle = search.strip().lower()
    haystacks = (
      record.audit_id,
      record.alias_id,
      record.action,
      record.template_key,
      record.template_label,
      record.redaction_policy,
      record.retention_policy,
      record.source_tab_id or "",
      record.source_tab_label or "",
      record.detail,
    )
    return any(needle in value.lower() for value in haystacks if value)

  def list_replay_intent_alias_audits(
    self,
    *,
    alias_id: str | None = None,
    template_key: str | None = None,
    action: str | None = None,
    retention_policy: str | None = None,
    source_tab_id: str | None = None,
    search: str | None = None,
    limit: int | None = 100,
  ) -> tuple[ReplayIntentAliasAuditRecord, ...]:
    self._prune_replay_intent_alias_audit_records()
    normalized_alias_id = alias_id.strip() if isinstance(alias_id, str) and alias_id.strip() else None
    normalized_template_key = (
      template_key.strip() if isinstance(template_key, str) and template_key.strip() else None
    )
    normalized_action = self._normalize_replay_intent_alias_audit_action(action)
    normalized_retention_policy = (
      self._normalize_replay_intent_alias_retention_policy(retention_policy)
      if isinstance(retention_policy, str) and retention_policy.strip()
      else None
    )
    normalized_source_tab_id = (
      source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None
    )
    normalized_limit = None if limit is None else max(1, min(limit, 5_000))
    filtered = [
      record
      for record in self._list_replay_intent_alias_audit_records(normalized_alias_id)
      if (normalized_template_key is None or record.template_key == normalized_template_key)
      and (normalized_action is None or record.action == normalized_action)
      and (
        normalized_retention_policy is None
        or record.retention_policy == normalized_retention_policy
      )
      and (
        normalized_source_tab_id is None
        or record.source_tab_id == normalized_source_tab_id
      )
      and self._matches_replay_intent_alias_audit_search(record, search)
    ]
    return tuple(filtered if normalized_limit is None else filtered[:normalized_limit])

  def create_replay_intent_alias_audit_export_job(
    self,
    *,
    export_format: str = "json",
    alias_id: str | None = None,
    template_key: str | None = None,
    action: str | None = None,
    retention_policy: str | None = None,
    source_tab_id: str | None = None,
    search: str | None = None,
    requested_by_tab_id: str | None = None,
    requested_by_tab_label: str | None = None,
  ) -> ReplayIntentAliasAuditExportJobRecord:
    self._prune_replay_intent_alias_audit_export_artifact_records()
    self._prune_replay_intent_alias_audit_export_job_records()
    self._prune_replay_intent_alias_audit_export_job_audit_records()
    export_payload = self.export_replay_intent_alias_audits(
      export_format=export_format,
      alias_id=alias_id,
      template_key=template_key,
      action=action,
      retention_policy=retention_policy,
      source_tab_id=source_tab_id,
      search=search,
    )
    created_at = self._clock()
    artifact_id = uuid4().hex[:12]
    artifact_record = ReplayIntentAliasAuditExportArtifactRecord(
      artifact_id=artifact_id,
      job_id=uuid4().hex[:12],
      filename=export_payload["filename"],
      content_type=export_payload["content_type"],
      content=export_payload["content"],
      created_at=created_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=created_at,
      ),
      byte_length=len(export_payload["content"].encode("utf-8")),
    )
    job_id = uuid4().hex[:12]
    saved_artifact = self._save_replay_intent_alias_audit_export_artifact_record(
      replace(artifact_record, job_id=job_id)
    )
    record = ReplayIntentAliasAuditExportJobRecord(
      job_id=job_id,
      export_format=export_payload["format"],
      filename=export_payload["filename"],
      content_type=export_payload["content_type"],
      record_count=int(export_payload["record_count"]),
      status="completed",
      created_at=created_at,
      completed_at=created_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=created_at,
      ),
      template_key=template_key.strip() if isinstance(template_key, str) and template_key.strip() else None,
      requested_by_tab_id=(
        requested_by_tab_id.strip()
        if isinstance(requested_by_tab_id, str) and requested_by_tab_id.strip()
        else None
      ),
      requested_by_tab_label=(
        requested_by_tab_label.strip()
        if isinstance(requested_by_tab_label, str) and requested_by_tab_label.strip()
        else None
      ),
      filters={
        "alias_id": alias_id,
        "template_key": template_key,
        "action": action,
        "retention_policy": retention_policy,
        "source_tab_id": source_tab_id,
        "search": search,
      },
      artifact_id=saved_artifact.artifact_id,
      content_length=saved_artifact.byte_length,
    )
    saved_record = self._save_replay_intent_alias_audit_export_job_record(record)
    self._record_replay_intent_alias_audit_export_job_event(
      record=saved_record,
      action="created",
      source_tab_id=requested_by_tab_id,
      source_tab_label=requested_by_tab_label,
    )
    return saved_record

  @classmethod
  def _matches_replay_intent_alias_audit_export_job_search(
    cls,
    record: ReplayIntentAliasAuditExportJobRecord,
    search: str | None,
  ) -> bool:
    if not isinstance(search, str) or not search.strip():
      return True
    needle = search.strip().lower()
    haystacks = (
      record.job_id,
      record.filename,
      record.export_format,
      record.status,
      record.template_key or "",
      record.requested_by_tab_id or "",
      record.requested_by_tab_label or "",
    )
    return any(needle in value.lower() for value in haystacks if value)

  def list_replay_intent_alias_audit_export_jobs(
    self,
    *,
    template_key: str | None = None,
    export_format: str | None = None,
    status: str | None = None,
    requested_by_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 100,
  ) -> tuple[ReplayIntentAliasAuditExportJobRecord, ...]:
    self._prune_replay_intent_alias_audit_export_artifact_records()
    self._prune_replay_intent_alias_audit_export_job_records()
    self._prune_replay_intent_alias_audit_export_job_audit_records()
    normalized_template_key = template_key.strip() if isinstance(template_key, str) and template_key.strip() else None
    normalized_export_format = export_format.strip().lower() if isinstance(export_format, str) and export_format.strip() else None
    normalized_status = status.strip().lower() if isinstance(status, str) and status.strip() else None
    normalized_requested_by_tab_id = (
      requested_by_tab_id.strip()
      if isinstance(requested_by_tab_id, str) and requested_by_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 500))
    search_value = search.strip().lower() if isinstance(search, str) and search.strip() else None
    filtered = [
      record
      for record in self._list_replay_intent_alias_audit_export_job_records()
      if (normalized_template_key is None or record.template_key == normalized_template_key)
      and (normalized_export_format is None or record.export_format == normalized_export_format)
      and (normalized_status is None or record.status == normalized_status)
      and (
        normalized_requested_by_tab_id is None
        or record.requested_by_tab_id == normalized_requested_by_tab_id
      )
      and self._matches_replay_intent_alias_audit_export_job_search(record, search_value)
    ]
    return tuple(filtered[:normalized_limit])

  def get_replay_intent_alias_audit_export_job(
    self,
    job_id: str,
  ) -> ReplayIntentAliasAuditExportJobRecord:
    self._prune_replay_intent_alias_audit_export_artifact_records()
    self._prune_replay_intent_alias_audit_export_job_records()
    normalized_job_id = job_id.strip()
    if not normalized_job_id:
      raise LookupError("Replay alias audit export job not found.")
    record = self._load_replay_intent_alias_audit_export_job_record(normalized_job_id)
    if record is None:
      raise LookupError("Replay alias audit export job not found.")
    if record.expires_at is not None and record.expires_at <= self._clock():
      raise LookupError("Replay alias audit export job has expired.")
    return record

  def get_replay_intent_alias_audit_export_artifact(
    self,
    artifact_id: str,
  ) -> ReplayIntentAliasAuditExportArtifactRecord:
    self._prune_replay_intent_alias_audit_export_artifact_records()
    normalized_artifact_id = artifact_id.strip()
    if not normalized_artifact_id:
      raise LookupError("Replay alias audit export artifact not found.")
    record = self._load_replay_intent_alias_audit_export_artifact_record(normalized_artifact_id)
    if record is None:
      raise LookupError("Replay alias audit export artifact not found.")
    if record.expires_at is not None and record.expires_at <= self._clock():
      raise LookupError("Replay alias audit export artifact has expired.")
    return record

  def list_replay_intent_alias_audit_export_job_history(
    self,
    job_id: str,
  ) -> tuple[ReplayIntentAliasAuditExportJobAuditRecord, ...]:
    record = self.get_replay_intent_alias_audit_export_job(job_id)
    self._prune_replay_intent_alias_audit_export_job_audit_records()
    return self._list_replay_intent_alias_audit_export_job_audit_records(record.job_id)

  def prune_replay_intent_alias_audit_export_jobs(
    self,
    *,
    template_key: str | None = None,
    export_format: str | None = None,
    status: str | None = None,
    requested_by_tab_id: str | None = None,
    search: str | None = None,
    created_before: datetime | None = None,
    prune_mode: str = "expired",
  ) -> dict[str, Any]:
    normalized_mode = prune_mode if prune_mode in {"expired", "matched"} else "expired"
    if normalized_mode == "expired":
      deleted_artifact_count = self._prune_replay_intent_alias_audit_export_artifact_records()
      deleted_job_count = self._prune_replay_intent_alias_audit_export_job_records()
      deleted_history_count = self._prune_replay_intent_alias_audit_export_job_audit_records()
      return {
        "deleted_artifact_count": deleted_artifact_count,
        "deleted_history_count": deleted_history_count,
        "deleted_job_count": deleted_job_count,
        "mode": "expired",
      }
    candidate_records = self.list_replay_intent_alias_audit_export_jobs(
      template_key=template_key,
      export_format=export_format,
      status=status,
      requested_by_tab_id=requested_by_tab_id,
      search=search,
      limit=500,
    )
    deleted_records = [
      record
      for record in candidate_records
      if created_before is None or record.created_at <= created_before
    ]
    deleted_job_ids = tuple(record.job_id for record in deleted_records)
    deleted_artifact_ids = tuple(
      record.artifact_id
      for record in deleted_records
      if isinstance(record.artifact_id, str) and record.artifact_id
    )
    deleted_history_ids = tuple(
      audit_record.audit_id
      for audit_record in self._list_replay_intent_alias_audit_export_job_audit_records()
      if audit_record.job_id in deleted_job_ids
    )
    deleted_artifact_count = self._delete_replay_intent_alias_audit_export_artifact_records(deleted_artifact_ids)
    deleted_history_count = self._delete_replay_intent_alias_audit_export_job_audit_records(deleted_history_ids)
    deleted_job_count = self._delete_replay_intent_alias_audit_export_job_records(deleted_job_ids)
    return {
      "deleted_artifact_count": deleted_artifact_count,
      "deleted_artifact_ids": list(deleted_artifact_ids),
      "deleted_history_count": deleted_history_count,
      "deleted_job_count": deleted_job_count,
      "deleted_job_ids": list(deleted_job_ids),
      "mode": "matched",
    }

  def prune_replay_intent_alias_audits(
    self,
    *,
    alias_id: str | None = None,
    template_key: str | None = None,
    action: str | None = None,
    retention_policy: str | None = None,
    source_tab_id: str | None = None,
    search: str | None = None,
    recorded_before: datetime | None = None,
    include_manual: bool = False,
    prune_mode: str = "expired",
  ) -> dict[str, Any]:
    normalized_mode = prune_mode if prune_mode in {"expired", "matched"} else "expired"
    if normalized_mode == "expired":
      deleted_count = self._prune_replay_intent_alias_audit_records()
      return {
        "deleted_count": deleted_count,
        "mode": "expired",
      }
    candidate_records = self.list_replay_intent_alias_audits(
      alias_id=alias_id,
      template_key=template_key,
      action=action,
      retention_policy=retention_policy,
      source_tab_id=source_tab_id,
      search=search,
      limit=500,
    )
    deleted_records = [
      record
      for record in candidate_records
      if (include_manual or record.retention_policy != "manual")
      and (recorded_before is None or record.recorded_at <= recorded_before)
    ]
    deleted_count = self._delete_replay_intent_alias_audit_records(
      tuple(record.audit_id for record in deleted_records)
    )
    return {
      "deleted_count": deleted_count,
      "matched_audit_ids": [record.audit_id for record in deleted_records],
      "mode": "matched",
    }

  def _get_replay_intent_alias_record_for_token(
    self,
    alias_token: str,
    *,
    require_active: bool = True,
  ) -> ReplayIntentAliasRecord:
    alias_id, supplied_signature = self._parse_replay_intent_alias_token(alias_token)
    self._prune_replay_intent_alias_records()
    record = self._load_replay_intent_alias_record(alias_id)
    if record is None:
      raise LookupError("Replay link alias not found.")
    expected_signature = self._build_replay_intent_alias_signature(
      alias_id=record.alias_id,
      created_at=record.created_at,
      expires_at=record.expires_at,
      intent=record.intent,
      redaction_policy=record.redaction_policy,
      template_key=record.template_key,
    )
    if (
      not supplied_signature
      or supplied_signature != record.signature
      or record.signature != expected_signature
    ):
      raise LookupError("Replay link alias not found.")
    if require_active:
      if record.revoked_at is not None:
        raise LookupError("Replay link alias has been revoked.")
      if record.expires_at is not None and record.expires_at <= self._clock():
        raise LookupError("Replay link alias has expired.")
    return record

  def create_replay_intent_alias(
    self,
    *,
    template_key: str,
    template_label: str | None,
    intent: dict[str, Any],
    redaction_policy: str,
    retention_policy: str,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ReplayIntentAliasRecord:
    normalized_template_key = template_key.strip()
    if not normalized_template_key:
      raise ValueError("Replay link aliases require a template key.")
    if not isinstance(intent, dict):
      raise ValueError("Replay link aliases require an intent payload object.")
    created_at = self._clock()
    normalized_retention_policy = self._normalize_replay_intent_alias_retention_policy(
      retention_policy
    )
    expires_at = self._build_replay_intent_alias_expiry(
      retention_policy=normalized_retention_policy,
      created_at=created_at,
    )
    alias_id = uuid4().hex[:10]
    normalized_intent = deepcopy(intent)
    signature = self._build_replay_intent_alias_signature(
      alias_id=alias_id,
      created_at=created_at,
      expires_at=expires_at,
      intent=normalized_intent,
      redaction_policy=self._normalize_replay_intent_alias_redaction_policy(redaction_policy),
      template_key=normalized_template_key,
    )
    record = ReplayIntentAliasRecord(
      alias_id=alias_id,
      signature=signature,
      template_key=normalized_template_key,
      template_label=(template_label or normalized_template_key).strip() or normalized_template_key,
      intent=normalized_intent,
      redaction_policy=self._normalize_replay_intent_alias_redaction_policy(redaction_policy),
      retention_policy=normalized_retention_policy,
      created_at=created_at,
      expires_at=expires_at,
      created_by_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      created_by_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
    )
    saved_record = self._save_replay_intent_alias_record(record)
    self._record_replay_intent_alias_audit_event(
      record=saved_record,
      action="created",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    return saved_record

  def get_replay_intent_alias(
    self,
    alias_token: str,
    *,
    require_active: bool = False,
  ) -> ReplayIntentAliasRecord:
    return self._get_replay_intent_alias_record_for_token(
      alias_token,
      require_active=require_active,
    )

  def resolve_replay_intent_alias(self, alias_token: str) -> ReplayIntentAliasRecord:
    record = self._get_replay_intent_alias_record_for_token(alias_token, require_active=True)
    self._record_replay_intent_alias_audit_event(record=record, action="resolved")
    return record

  def revoke_replay_intent_alias(
    self,
    alias_token: str,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ReplayIntentAliasRecord:
    record = self._get_replay_intent_alias_record_for_token(alias_token, require_active=False)
    if record.revoked_at is not None:
      return record
    revoked_record = replace(
      record,
      revoked_at=self._clock(),
      revoked_by_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      revoked_by_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
    )
    saved_record = self._save_replay_intent_alias_record(revoked_record)
    self._record_replay_intent_alias_audit_event(
      record=saved_record,
      action="revoked",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    return saved_record

  def list_replay_intent_alias_history(
    self,
    alias_token: str,
  ) -> tuple[ReplayIntentAliasAuditRecord, ...]:
    record = self.get_replay_intent_alias(alias_token, require_active=False)
    self._prune_replay_intent_alias_audit_records()
    return self._list_replay_intent_alias_audit_records(record.alias_id)
