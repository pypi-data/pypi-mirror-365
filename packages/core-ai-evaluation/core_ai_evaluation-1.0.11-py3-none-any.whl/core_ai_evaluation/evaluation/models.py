from dataclasses import dataclass


@dataclass
class ModelInput:
    subject: str | None
    input: str
    references: list[str] | None


@dataclass
class Answer:
    subject: str | None
    input: str
    output: str | None
    references: list[str] | None


@dataclass
class Score:
    bert_precision: float | None
    bert_recall: float | None
    bert_f1: float | None
    deepeval_answer_relevancy: float | None
    deepeval_custom_metric_general: float | None
    deepeval_custom_metric_dataset: float | None


@dataclass
class ScoreBatch:
    bert_precision: list[float | None]
    bert_recall: list[float | None]
    bert_f1: list[float | None]
    deepeval_answer_relevancy: list[float | None]
    deepeval_custom_metric_general: float | None
    deepeval_custom_metric_dataset: float | None


@dataclass
class Metrics:
    bert_precision: float | None
    bert_recall: float | None
    bert_f1: float | None
    deepeval_answer_relevancy: float | None
    deepeval_custom_metric_general: float | None
    deepeval_custom_metric_dataset: float | None


@dataclass
class Result:
    answer: Answer
    score: Score
