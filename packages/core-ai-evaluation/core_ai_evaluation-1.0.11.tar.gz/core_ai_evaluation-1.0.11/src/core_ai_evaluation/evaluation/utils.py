from collections import defaultdict

import numpy as np
import pandas as pd

from core_ai_evaluation.evaluation.models import ModelInput, Result


def prepare_data(dataset: pd.DataFrame) -> list[ModelInput]:
    model_inputs = [
        ModelInput(row["subject"], row["input"], row["reference"])
        for index, row in dataset.iterrows()
    ]
    return model_inputs


def calc_metrics_from_scores(results: list[Result]) -> dict[str, dict[str, float]]:
    bert_precision = [result.score.bert_precision for result in results]
    bert_recall = [result.score.bert_recall for result in results]
    bert_f1 = [result.score.bert_f1 for result in results]
    deepeval_answer_relevancy = [
        result.score.deepeval_answer_relevancy for result in results
    ]
    deepeval_custom_metric_general = [
        result.score.deepeval_custom_metric_general for result in results
    ]
    deepeval_custom_metric_dataset = [
        result.score.deepeval_custom_metric_dataset for result in results
    ]
    subjects = [result.answer.subject for result in results]

    # Zip all the metric lists together with subject
    zipped = zip(
        subjects,
        bert_precision,
        bert_recall,
        bert_f1,
        deepeval_answer_relevancy,
        deepeval_custom_metric_general,
        deepeval_custom_metric_dataset,
        strict=False,
    )

    # Group scores by subject
    grouped = defaultdict(
        lambda: {
            "bert_precision": [],
            "bert_recall": [],
            "bert_f1": [],
            "deepeval_answer_relevancy": [],
            "deepeval_custom_metric_general": [],
            "deepeval_custom_metric_dataset": [],
        }
    )

    for subject, bp, br, bf1, dar, dcmg, dcmd in zipped:
        grouped[subject]["bert_precision"].append(bp)
        grouped[subject]["bert_recall"].append(br)
        grouped[subject]["bert_f1"].append(bf1)
        grouped[subject]["deepeval_answer_relevancy"].append(dar)
        grouped[subject]["deepeval_custom_metric_general"].append(dcmg)
        grouped[subject]["deepeval_custom_metric_dataset"].append(dcmd)

    # Compute averages
    averaged = {
        subject: {
            metric: safe_round(safe_mean(values)) for metric, values in scores.items()
        }
        for subject, scores in grouped.items()
    }
    return averaged


def safe_mean(values: list[float | None]) -> float | None:
    cleaned = [v for v in values if v is not None]
    return np.mean(cleaned) if cleaned else None


def safe_round(value: float | None, num_digits: int = 5) -> float | None:
    rounded_value = round(value, num_digits) if value is not None else None
    return rounded_value
