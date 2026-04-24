from __future__ import annotations

from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterConstraintSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOpenAPISpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding


def build_replay_link_runtime_bindings() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  replay_alias_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_create",
    route_path="/replay-links/aliases",
    route_name="create_replay_link_alias",
    response_title="Create replay link alias",
    scope="app",
    binding_kind="replay_link_alias_create",
    methods=("POST",),
    request_payload_kind="replay_link_alias_create",
  )
  replay_alias_resolve_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_resolve",
    route_path="/replay-links/aliases/{alias_token}",
    route_name="resolve_replay_link_alias",
    response_title="Resolve replay link alias",
    scope="app",
    binding_kind="replay_link_alias_resolve",
    path_param_keys=("alias_token",),
  )
  replay_alias_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_history",
    route_path="/replay-links/aliases/{alias_token}/history",
    route_name="get_replay_link_alias_history",
    response_title="Replay link alias history",
    scope="app",
    binding_kind="replay_link_alias_history",
    path_param_keys=("alias_token",),
  )
  replay_alias_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_list",
    route_path="/replay-links/audits",
    route_name="list_replay_link_alias_audits",
    response_title="List replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_list",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("alias_id", "template_key", "action", "retention_policy", "source_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "alias_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Alias ID",
          description="Filter replay alias audits by alias identifier.",
          examples=("abc123def4",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audits by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Audit action",
          description="Filter replay alias audits by action kind.",
          examples=("revoked",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "retention_policy",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Retention policy",
          description="Filter replay alias audits by retention policy.",
          examples=("7d",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab ID",
          description="Filter replay alias audits by source tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit ids, template labels, source tabs, and detail text.",
          examples=("Remote tab",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=100,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=500),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of replay alias audit records to return.",
          examples=(50,),
        ),
      ),
    ),
  )
  replay_alias_audit_export_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export",
    route_path="/replay-links/audits/export",
    route_name="export_replay_link_alias_audits",
    response_title="Export replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_export",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("alias_id", "template_key", "action", "retention_policy", "source_tab_id", "search", "format"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "alias_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Alias ID",
          description="Filter replay alias audit export by alias identifier.",
          examples=("abc123def4",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audit export by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Audit action",
          description="Filter replay alias audit export by action kind.",
          examples=("revoked",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "retention_policy",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Retention policy",
          description="Filter replay alias audit export by retention policy.",
          examples=("7d",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab ID",
          description="Filter replay alias audit export by source tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit export ids, template labels, source tabs, and detail text.",
          examples=("Remote tab",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "format",
        str,
        default="json",
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3, max_length=4),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Export format",
          description="Replay alias audit export format.",
          examples=("json", "csv"),
        ),
      ),
    ),
  )
  replay_alias_audit_export_job_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_create",
    route_path="/replay-links/audits/export-jobs",
    route_name="create_replay_link_alias_audit_export_job",
    response_title="Create replay link alias audit export job",
    scope="app",
    binding_kind="replay_link_audit_export_job_create",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_export_job_create",
  )
  replay_alias_audit_export_job_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_list",
    route_path="/replay-links/audits/export-jobs",
    route_name="list_replay_link_alias_audit_export_jobs",
    response_title="List replay link alias audit export jobs",
    scope="app",
    binding_kind="replay_link_audit_export_job_list",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("template_key", "format", "status", "requested_by_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audit export jobs by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "format",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3, max_length=4),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Export format",
          description="Filter replay alias audit export jobs by export format.",
          examples=("json", "csv"),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Job status",
          description="Filter replay alias audit export jobs by status.",
          examples=("completed",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "requested_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Requested by tab ID",
          description="Filter replay alias audit export jobs by requesting tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit export job ids, filenames, formats, and requester labels.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=100,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=500),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of replay alias audit export jobs to return.",
          examples=(25,),
        ),
      ),
    ),
  )
  replay_alias_audit_export_job_download_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_download",
    route_path="/replay-links/audits/export-jobs/{job_id}/download",
    route_name="download_replay_link_alias_audit_export_job",
    response_title="Download replay link alias audit export job",
    scope="app",
    binding_kind="replay_link_audit_export_job_download",
    header_keys=("x_akra_replay_audit_admin_token",),
    path_param_keys=("job_id",),
  )
  replay_alias_audit_export_job_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_history",
    route_path="/replay-links/audits/export-jobs/{job_id}/history",
    route_name="get_replay_link_alias_audit_export_job_history",
    response_title="Replay link alias audit export job history",
    scope="app",
    binding_kind="replay_link_audit_export_job_history",
    header_keys=("x_akra_replay_audit_admin_token",),
    path_param_keys=("job_id",),
  )
  replay_alias_audit_export_job_prune_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_prune",
    route_path="/replay-links/audits/export-jobs/prune",
    route_name="prune_replay_link_alias_audit_export_jobs",
    response_title="Prune replay link alias audit export jobs",
    scope="app",
    binding_kind="replay_link_audit_export_job_prune",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_export_job_prune",
  )
  replay_alias_audit_prune_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_prune",
    route_path="/replay-links/audits/prune",
    route_name="prune_replay_link_alias_audits",
    response_title="Prune replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_prune",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_prune",
  )
  replay_alias_revoke_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_revoke",
    route_path="/replay-links/aliases/{alias_token}/revoke",
    route_name="revoke_replay_link_alias",
    response_title="Revoke replay link alias",
    scope="app",
    binding_kind="replay_link_alias_revoke",
    methods=("POST",),
    path_param_keys=("alias_token",),
    request_payload_kind="replay_link_alias_revoke",
  )
  return (
    replay_alias_create_binding,
    replay_alias_resolve_binding,
    replay_alias_history_binding,
    replay_alias_audit_list_binding,
    replay_alias_audit_export_binding,
    replay_alias_audit_export_job_create_binding,
    replay_alias_audit_export_job_list_binding,
    replay_alias_audit_export_job_download_binding,
    replay_alias_audit_export_job_history_binding,
    replay_alias_audit_export_job_prune_binding,
    replay_alias_audit_prune_binding,
    replay_alias_revoke_binding,
  )
