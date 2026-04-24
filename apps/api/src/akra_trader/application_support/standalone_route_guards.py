from __future__ import annotations

from hmac import compare_digest


def _token_matches(presented_token: str | None, expected_token: str | None) -> bool:
  return bool(
    presented_token
    and expected_token
    and compare_digest(presented_token, expected_token)
  )


def require_replay_alias_audit_admin_token(
  presented_token: str | None,
  *,
  scope: str,
  read_token: str | None,
  write_token: str | None,
) -> None:
  if scope == "read":
    allowed_tokens = (read_token, write_token)
  elif scope == "write":
    allowed_tokens = (write_token,)
  else:
    raise ValueError(f"Unsupported replay alias audit admin token scope: {scope}")

  if any(_token_matches(presented_token, allowed_token) for allowed_token in allowed_tokens):
    return
  raise PermissionError("invalid replay alias audit admin token")


def require_operator_alert_external_sync_token(
  presented_token: str | None,
  *,
  expected_token: str | None,
) -> None:
  if _token_matches(presented_token, expected_token):
    return
  raise PermissionError("invalid operator alert external sync token")
