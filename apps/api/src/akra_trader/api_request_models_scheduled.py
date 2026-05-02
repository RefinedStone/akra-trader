from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

class OperatorProviderProvenanceScheduledReportCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  layout: dict[str, Any] = Field(default_factory=dict)
  preset_id: str | None = None
  view_id: str | None = None
  cadence: str = "daily"
  status: str = "scheduled"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceScheduledReportRunRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceScheduledReportRunDueRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  due_before: datetime | None = None
  limit: int = Field(default=25, ge=1, le=100)
