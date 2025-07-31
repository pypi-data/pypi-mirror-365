from core_ai_evaluation.api.answer_generator import AnswerGenerator
from core_ai_evaluation.configuration import get_available_providers
from core_ai_evaluation.evaluation.dataset_loader import DatasetLoader
from core_ai_evaluation.evaluation.evaluation_model import EvaluationModel
from core_ai_evaluation.evaluation.evaluator import Evaluator
from core_ai_evaluation.evaluation.utils import calc_metrics_from_scores, prepare_data
from core_ai_evaluation.shared.log import logger


class EvaluationService:
    eval_model: EvaluationModel = None

    def load_evaluation_model(self):
        if self.eval_model is None:
            providers = get_available_providers()
            provider = providers[0]
            logger.info(f"Loading evaluation model from {provider.__class__.__name__}")
            chat_model = provider.get_chat_model(
                model_name=provider.default_model, temperature=0
            )
            self.eval_model = EvaluationModel(chat_model)

    async def run(self, answer_generator: AnswerGenerator):
        # Load Datasets
        self.load_evaluation_model()
        logger.info("1/5: Loading Test Data")
        df = DatasetLoader.load_all(num_subjects=5, num_questions_per_subject=3)
        # Transform Dataframe to objects of class ModelInput
        logger.info("2/5: Tranform Raw Data To Model Input...")
        model_inputs = prepare_data(df)

        # Generate Agent Output
        logger.info("3/5: Generate Agent Output...")
        answers = [await answer_generator.generate(x) for x in model_inputs]

        # Calculate Evaluation Scores
        logger.info("4/5: Evaluate Agent Output...")
        evaluator = Evaluator(self.eval_model)
        results = list(map(evaluator.evaluate, answers))

        # Determine Handover Metrics
        logger.info("5/5: Calculate Metrics...")
        metrics = calc_metrics_from_scores(results)
        output_lines = []

        for subject, scores in metrics.items():
            output_lines.append(f"Subject: {subject}")
            output_lines.append(f"  - BERT Precision: {scores['bert_precision']:.3f}")
            output_lines.append(f"  - BERT Recall:    {scores['bert_recall']:.3f}")
            output_lines.append(f"  - BERT F1:        {scores['bert_f1']:.3f}")
            output_lines.append(
                f"  - Deepeval Custom Metric (task-specific):        {scores['deepeval_custom_metric_dataset']:.3f}"
            )
            output_lines.append("")  # Add a blank line between subjects

        result_str = "\n".join(output_lines)
        print(result_str)

        logger.info(f"Scores: {result_str}")

        return f"Scores: {result_str}"


evaluation_service = EvaluationService()
