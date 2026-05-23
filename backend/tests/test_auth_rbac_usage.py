import pytest

from app.config import Settings
from app.dependencies import RequestContext, require_permission, verify_clerk_token
from app.services.usage_service import UsageService
from app.utils.errors import AuthError, BriefToScopeError


@pytest.mark.asyncio
async def test_missing_clerk_jwt_returns_401_outside_demo_mode():
    with pytest.raises(AuthError) as exc:
        await verify_clerk_token(credentials=None, settings=Settings(demo_mode=False))

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_rbac_denies_reviewer_pdf_export():
    dependency = require_permission("sow:export")
    context = RequestContext(
        clerk_user_id="user_clerk",
        email="reviewer@example.com",
        name="Reviewer",
        user_id="user-1",
        org_id="org-1",
        role="reviewer",
        plan="studio",
        subscription_status="active",
    )

    with pytest.raises(BriefToScopeError) as exc:
        await dependency(context)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_quota_exhaustion_blocks_before_provider_call(monkeypatch):
    service = UsageService()

    async def used_up(*args, **kwargs):
        return 3

    service.storage.sum_usage_events = used_up

    with pytest.raises(BriefToScopeError) as exc:
        await service.assert_quota_available("org-1", "free", "active", "sow_generated")

    assert exc.value.status_code == 402
    assert "quota" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_inactive_subscription_blocks_expensive_action():
    service = UsageService()

    with pytest.raises(BriefToScopeError) as exc:
        await service.assert_quota_available("org-1", "agency", "past_due", "pdf_export")

    assert exc.value.status_code == 402
    assert "subscription" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_feature_not_included_blocks_esign_on_free_plan():
    service = UsageService()

    with pytest.raises(BriefToScopeError) as exc:
        await service.assert_quota_available("org-1", "free", "active", "esign_request")

    assert exc.value.status_code == 402
    assert "not included" in exc.value.message.lower()
