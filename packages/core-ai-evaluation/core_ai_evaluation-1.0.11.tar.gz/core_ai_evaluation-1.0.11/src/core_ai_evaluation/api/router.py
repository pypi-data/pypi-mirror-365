import uuid

from fastapi import APIRouter, BackgroundTasks
from starlette import status

from core_ai_evaluation.api.answer_generator import AnswerGenerator
from core_ai_evaluation.api.models import EvaluationRequest
from core_ai_evaluation.evaluation.service import evaluation_service
from core_ai_evaluation.shared.log import logger

router = APIRouter(prefix="/api/evaluation")


async def _run_and_handle(generator: AnswerGenerator, job_id: str):
    try:
        await evaluation_service.run(generator)
        logger.info(f"Job {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Error in Evaluation Service for job {job_id}: {e}")


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def evaluate(request: EvaluationRequest, background_tasks: BackgroundTasks):
    generator = AnswerGenerator(
        chat_model=request.chat_model,
        temperature=request.temperature,
        system_instructions=request.system_instructions,
    )
    job_id = str(uuid.uuid4())
    background_tasks.add_task(_run_and_handle, generator, job_id)

    return {"job_id": job_id, "status": "accepted"}
