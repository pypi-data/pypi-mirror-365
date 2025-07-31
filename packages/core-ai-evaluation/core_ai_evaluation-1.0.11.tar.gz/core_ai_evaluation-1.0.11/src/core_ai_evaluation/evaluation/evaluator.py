import bert_score
from deepeval import metrics, test_case

from core_ai_evaluation.evaluation.evaluation_model import EvaluationModel
from core_ai_evaluation.evaluation.models import Answer, Result, Score
from core_ai_evaluation.evaluation.utils import safe_round
from core_ai_evaluation.shared.log import logger


class Evaluator:
    def __init__(self, eval_model: EvaluationModel):
        self.answer_relevancy_metric = metrics.AnswerRelevancyMetric(model=eval_model)

        # Custom Metric across all tasks
        self.custom_metric_general = metrics.GEval(
            model=eval_model,
            threshold=0.8,
            name="Conciseness",
            criteria="Determine whether the actual output is short and clear, and expresses what needs to be said without unnecessary words.",
            evaluation_params=[
                test_case.LLMTestCaseParams.INPUT,
                test_case.LLMTestCaseParams.ACTUAL_OUTPUT,
                test_case.LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
        )

        # TEST for MMLU
        self.custom_metric_mmlu = metrics.GEval(
            model=eval_model,
            threshold=0.8,
            name="Correctness MMLU",
            criteria="Determine if the Actual Output (the chosen answer option) matches the Expected Output (the correct answer label/text). The Actual Output can include additional information but it is correct so long as it include the Expected Output.",
            evaluation_steps=[
                "Read the Input Question and the provided Answer Options carefully.",
                "Compare the Actual Output (model's chosen answer) with the Expected Output (correct answer label/text).",
                "Assess if the statement of the Actual Output matches the statement of the Expected Output.",
                "Based only on Correctness (matching the Expected Output), provide a score on the continuous scale between 0 (Incorrect) and 1 (Correct).",
            ],
            evaluation_params=[
                test_case.LLMTestCaseParams.INPUT,
                test_case.LLMTestCaseParams.ACTUAL_OUTPUT,
                test_case.LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
        )

        # TEST for XSUM
        self.custom_metric_xsum = metrics.GEval(
            model=eval_model,
            threshold=0.8,
            name="Correctness XSUM",
            criteria="""
                Faithfulness and Relevance:
                1. **Faithfulness:** Does the Actual Output (summary) accurately represent the main point(s) of the Input Document without introducing factual errors or information not present in the source?
                2. **Relevance:** Does the Actual Output capture the absolute core essence or the most critical information from the Input Document?
            """,
            evaluation_steps=[
                "Read the Input Document carefully to understand its main points.",
                "Read the Actual Output (generated summary).",
                "Evaluate the summary based on the two cirteria: Faithfulness and Relevance.",
                "Assign a score from 0 to 1, considering all criteria holistically.",
                "A score of 1 requires the summary to be highly faithful, extremely concise (like one sentence), relevant to the main point, and fluent.",
                "A score below 0.5 indicates significant issues in faithfulness or conciseness.",
            ],
            evaluation_params=[
                test_case.LLMTestCaseParams.INPUT,
                test_case.LLMTestCaseParams.ACTUAL_OUTPUT,
                test_case.LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
        )

        # TEST for HellaSwag
        self.custom_metric_hellaswag = metrics.GEval(
            model=eval_model,
            threshold=0.8,
            name="Correctness HellaSwag",
            criteria="Does the Actual Output match the Expected Output (the known correct ending)?",
            evaluation_steps=[
                "Read the Input Context (the beginning of the scenario) carefully.",
                "Read the Actual Output (the ending chosen by the model).",
                "Read the Expected Output (the correct ending).",
                "Determine if the Actual Output exactly matches the Expected Output.",
                "Assign a score based ONLY on whether the Actual Output matches the Expected Output, with 1 being the best and 0 the worst.",
            ],
            evaluation_params=[
                test_case.LLMTestCaseParams.INPUT,
                test_case.LLMTestCaseParams.ACTUAL_OUTPUT,
                test_case.LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
        )

    def evaluate(self, answer: Answer) -> Result:
        try:
            P, R, F1 = bert_score.score(
                [answer.output],
                [answer.references],
                lang="en",
                verbose=False,
            )
            P, R, F1 = P.item(), R.item(), F1.item()
        except Exception as e:
            logger.error(f"BERTScore Error: {e}")
            P, R, F1 = None, None, None

        logger.info(f"Task Subject: {answer.subject}, Prec: {P}, Rec: {R}, F1: {F1}")
        test_case_temp = test_case.LLMTestCase(
            input=answer.input,
            actual_output=answer.output,
            expected_output=answer.references,
        )

        try:
            self.answer_relevancy_metric.measure(test_case_temp)
            self.custom_metric_general.measure(test_case_temp)

            deep_rel = self.answer_relevancy_metric.score
            deep_custom_metric_general = self.custom_metric_general.score

            if answer.subject == "hellaswag":
                self.custom_metric_hellaswag.measure(test_case_temp)
                deep_custom_metric_dataset = self.custom_metric_hellaswag.score
            elif answer.subject == "summarization":
                self.custom_metric_xsum.measure(test_case_temp)
                deep_custom_metric_dataset = self.custom_metric_xsum.score
            else:
                self.custom_metric_mmlu.measure(test_case_temp)
                deep_custom_metric_dataset = self.custom_metric_mmlu.score

        except Exception as e:
            logger.error(f"DeepEval Error: {e}")
            (
                deep_rel,
                deep_custom_metric_general,
                deep_custom_metric_dataset,
            ) = (None, None, None)

        score = Score(
            safe_round(P),
            safe_round(R),
            safe_round(F1),
            safe_round(deep_rel),
            safe_round(deep_custom_metric_general),
            safe_round(deep_custom_metric_dataset),
        )
        result = Result(answer, score)

        return result
