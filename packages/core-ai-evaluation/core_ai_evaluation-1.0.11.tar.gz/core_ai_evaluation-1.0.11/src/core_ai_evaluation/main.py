from dotenv import load_dotenv
from fastapi import FastAPI

from core_ai_evaluation.api.router import router
from core_ai_evaluation.shared.log import logger
from core_ai_evaluation.shared.setup_helper import verify_env_vars_are_correctly_setup
from core_ai_evaluation.shared.utils import get_version

load_dotenv()
app = FastAPI(title="Evaluation", version=get_version())
app.include_router(router)

if not verify_env_vars_are_correctly_setup():
    logger.error("Environment variables are not set up correctly.")
