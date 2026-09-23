from .models import AuditLog


def record_audit_log(
    *,
    user=None,
    action,
    module=None,
    instance=None,
    entity_type=None,
    entity_id=None,
    entity_repr=None,
    description="",
    metadata=None,
):

    if instance is not None:

        module = (
            module
            or instance._meta.app_label
        )

        entity_type = (
            entity_type
            or instance._meta.label
        )

        entity_id = (
            entity_id
            or str(instance.pk or "")
        )

        entity_repr = (
            entity_repr
            or str(instance)
        )

    if not module:
        raise ValueError(
            "Audit log module is required."
        )

    if not entity_type:
        raise ValueError(
            "Audit log entity_type is required."
        )

    actor = None

    if (
        user is not None
        and getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        actor = user

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        module=module,
        entity_type=entity_type,
        entity_id=str(
            entity_id or ""
        ),
        entity_repr=(
            entity_repr or ""
        ),
        description=description,
        metadata=metadata or {},
    )