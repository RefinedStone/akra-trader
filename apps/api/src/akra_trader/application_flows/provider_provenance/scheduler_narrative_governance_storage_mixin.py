from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import hashlib
import io
import json
import math
from numbers import Number
import re
from typing import Any
from typing import Mapping
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSchedulerNarrativeGovernanceStorageMixin:
  def _save_provider_provenance_scheduler_narrative_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    save_template = getattr(self._runs, "save_provider_provenance_scheduler_narrative_template", None)
    if callable(save_template):
      return save_template(record)
    self._provider_provenance_scheduler_narrative_templates[record.template_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_template_record(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord | None:
    get_template = getattr(self._runs, "get_provider_provenance_scheduler_narrative_template", None)
    if callable(get_template):
      return get_template(template_id)
    return self._provider_provenance_scheduler_narrative_templates.get(template_id)
  def _list_provider_provenance_scheduler_narrative_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...]:
    list_templates = getattr(self._runs, "list_provider_provenance_scheduler_narrative_templates", None)
    if callable(list_templates):
      return tuple(list_templates())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_templates.values(),
        key=lambda record: (record.updated_at, record.template_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_narrative_template_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_narrative_template_revisions[record.revision_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_narrative_template_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_narrative_template_revisions.get(revision_id)
  def _list_provider_provenance_scheduler_narrative_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_narrative_template_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_registry_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    save_registry_entry = getattr(self._runs, "save_provider_provenance_scheduler_narrative_registry_entry", None)
    if callable(save_registry_entry):
      return save_registry_entry(record)
    self._provider_provenance_scheduler_narrative_registry[record.registry_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_registry_record(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord | None:
    get_registry_entry = getattr(self._runs, "get_provider_provenance_scheduler_narrative_registry_entry", None)
    if callable(get_registry_entry):
      return get_registry_entry(registry_id)
    return self._provider_provenance_scheduler_narrative_registry.get(registry_id)
  def _list_provider_provenance_scheduler_narrative_registry_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...]:
    list_registry = getattr(self._runs, "list_provider_provenance_scheduler_narrative_registry_entries", None)
    if callable(list_registry):
      return tuple(list_registry())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_registry_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_narrative_registry_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_narrative_registry_revisions[record.revision_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_registry_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_narrative_registry_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_narrative_registry_revisions.get(revision_id)
  def _list_provider_provenance_scheduler_narrative_registry_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_narrative_registry_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )
  @staticmethod
  def _uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
    item_type_scope: str | None,
  ) -> bool:
    return item_type_scope == "stitched_report_governance_registry"
  @staticmethod
  def _uses_provider_provenance_scheduler_stitched_report_governance_plan_store(
    item_type: str | None,
  ) -> bool:
    return item_type == "stitched_report_governance_registry"
  def _save_provider_provenance_scheduler_narrative_governance_policy_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_templates[
        record.policy_template_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_templates[record.policy_template_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_policy_template_record(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_template",
      None,
    )
    if callable(get_record):
      record = get_record(policy_template_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_templates.get(policy_template_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_template",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(policy_template_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_templates.get(
      policy_template_id
    )
  def _list_provider_provenance_scheduler_narrative_governance_policy_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_templates",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_templates.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_templates",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_templates.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.policy_template_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template_revision",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions[
        record.revision_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions[record.revision_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_template_revision",
      None,
    )
    if callable(get_record):
      record = get_record(revision_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.get(
        revision_id
      )
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_template_revision",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.get(
      revision_id
    )
  def _list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_template_revisions",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_template_revisions",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_record",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records[
        record.audit_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records[record.audit_id] = record
    return record
  def _list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates[
      record.hierarchy_step_template_id
    ] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
      None,
    )
    if callable(get_record):
      return get_record(hierarchy_step_template_id)
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.get(
      hierarchy_step_template_id
    )
  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.values(),
        key=lambda record: (record.updated_at, record.hierarchy_step_template_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions[
      record.revision_id
    ] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision",
      None,
    )
    if callable(get_record):
      return get_record(revision_id)
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.get(
      revision_id
    )
  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records[
      record.audit_id
    ] = record
    return record
  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs[
        record.catalog_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs[record.catalog_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_catalog",
      None,
    )
    if callable(get_record):
      record = get_record(catalog_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_catalogs.get(catalog_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_catalog",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(catalog_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.get(catalog_id)
  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalogs",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalogs.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalogs",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.catalog_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions[
        record.revision_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions[record.revision_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_catalog_revision",
      None,
    )
    if callable(get_record):
      record = get_record(revision_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.get(
        revision_id
      )
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.get(
      revision_id
    )
  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_record",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records[
        record.audit_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records[record.audit_id] = (
      record
    )
    return record
  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )
  def _save_provider_provenance_scheduler_narrative_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_plan_store(record.item_type):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_plan",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_plans[record.plan_id] = record
      return record
    save_record = getattr(self._runs, "save_provider_provenance_scheduler_narrative_governance_plan", None)
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_plans[record.plan_id] = record
    return record
  def _load_provider_provenance_scheduler_narrative_governance_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None:
    get_record = getattr(self._runs, "get_provider_provenance_scheduler_narrative_governance_plan", None)
    if callable(get_record):
      record = get_record(plan_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_plans.get(plan_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_plan",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(plan_id)
    return self._provider_provenance_scheduler_stitched_report_governance_plans.get(plan_id)
  def _list_provider_provenance_scheduler_narrative_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    list_records = getattr(self._runs, "list_provider_provenance_scheduler_narrative_governance_plans", None)
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_plans.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_plans",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_plans.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )
