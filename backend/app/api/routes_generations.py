import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import RequestContext, require_permission
from app.models.production_schemas import GenerationCreateRequest, GenerationJobResponse
from app.services.generation_job_service import GenerationJobService
from app.workers.dispatcher import dispatch_generation_job

router = APIRouter(prefix="/api/generations", tags=["Generations"])


@router.post("", response_model=GenerationJobResponse)
async def create_generation(
    req: GenerationCreateRequest,
    background_tasks: BackgroundTasks,
    context: RequestContext = Depends(require_permission("sow:generate")),
):
    service = GenerationJobService()
    job = await service.create_job(req, context)
    try:
        dispatched = dispatch_generation_job(job["id"])
    except RuntimeError as exc:
        await service.mark_failed(job["id"], str(exc))
        raise HTTPException(status_code=503, detail=str(exc))
    if not dispatched:
        background_tasks.add_task(service.run_job, job["id"])
    return job


@router.get("/{generation_id}", response_model=GenerationJobResponse)
async def get_generation(
    generation_id: str,
    context: RequestContext = Depends(require_permission("sow:view")),
):
    job = await GenerationJobService().get_job(generation_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    if job.get("org_id") != context.org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this generation job")
    return job


@router.get("/{generation_id}/events")
async def stream_generation_events(
    generation_id: str,
    context: RequestContext = Depends(require_permission("sow:view")),
):
    initial_job = await GenerationJobService().get_job(generation_id)
    if not initial_job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    if initial_job.get("org_id") != context.org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this generation job")

    async def event_stream():
        service = GenerationJobService()
        last_index = 0
        for _ in range(300):
            events = await service.get_events(generation_id)
            for event in events[last_index:]:
                yield f"data: {json.dumps(event)}\n\n"
            last_index = len(events)
            job = await service.get_job(generation_id)
            if job and job["status"] in {"completed", "failed"}:
                yield f"data: {json.dumps({'step': job['status'], 'status': job['status'], 'progress': job['progress'], 'sow_id': job.get('sow_id')})}\n\n"
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
