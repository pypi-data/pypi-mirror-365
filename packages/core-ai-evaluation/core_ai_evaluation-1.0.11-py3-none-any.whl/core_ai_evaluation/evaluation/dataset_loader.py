from datetime import datetime

import pandas as pd

from core_ai_evaluation.shared.log import logger


class DatasetLoader:
    @staticmethod
    def load_all(
        num_subjects: int | None, num_questions_per_subject: int | None = 3
    ) -> pd.DataFrame:
        timestamp_start = datetime.now().timestamp()
        datasets = ["mmlu", "xsum", "hellaswag"]
        gcs_bucket_path = "gs://codify-data-ai-playground-core-ai-application/test-data"

        try:
            logger.info("Try loading test data from local file system...")
            mmlu = pd.read_csv(f"public/{datasets[0]}.csv")
            xsum = pd.read_csv(f"public/{datasets[1]}.csv")
            hellaswag = pd.read_csv(f"public/{datasets[2]}.csv")
            df = pd.concat([xsum, hellaswag, mmlu], ignore_index=True)
            logger.info(f"Loaded {df.shape[0]} rows from local file system.")
        except Exception as e:
            logger.warning(
                f"No test data available in 'public/'! Error: {e}. Try loading data from GCS..."
            )
            mmlu = pd.read_csv(f"{gcs_bucket_path}/{datasets[0]}.csv")
            xsum = pd.read_csv(f"{gcs_bucket_path}/{datasets[1]}.csv")
            hellaswag = pd.read_csv(f"{gcs_bucket_path}/{datasets[2]}.csv")
            df = pd.concat([xsum, hellaswag, mmlu], ignore_index=True)
            logger.info(f"Loaded {df.shape[0]} rows from GCS.")

        timestamp_end = datetime.now().timestamp()
        load_timespan = timestamp_end - timestamp_start
        df = df[["input", "reference", "subject"]]

        if num_subjects:
            subjects = df["subject"].unique()
            selected_subjects = subjects[
                : min(num_subjects, len(df["subject"].unique()))
            ]
            filtered_df = df[df["subject"].isin(selected_subjects)]
            # Group by subject and sample questions from each group
            sampled_questions = filtered_df.groupby("subject", group_keys=False).apply(
                lambda x: x.sample(
                    n=min(num_questions_per_subject, len(x)), random_state=42
                )
            )
        else:
            sampled_questions = df.groupby("subject", group_keys=False).apply(
                lambda x: x.sample(
                    n=min(num_questions_per_subject, len(x)), random_state=42
                )
            )

        # Reset index if needed
        sampled_questions = sampled_questions.reset_index(drop=True)

        logger.info(
            f"Took {load_timespan} sec to load the dataset of size {sampled_questions.shape}..."
        )

        return sampled_questions
