"""LLM judge for metrics."""

from portia import Config, Message

from steelthread.metrics.metric import Metric, MetricList


class LLMMetricScorer:
    """An implementation of an LLM as Judge to return metrics.

    Uses a configured LLM to score a list of metrics against task data, returning scores
    with optional explanations.
    """

    def __init__(
        self,
        config: Config,
        base_prompt: str = """You are an expert reviewer charged with evaluating agentic executions.
        For each metric provided please provide a score between 0 and 1 based on the data and task
        provided. IMPORTANT - Also include an explanation as to why you score it this way.""",
    ) -> None:
        """Initialize the LLMMetricScorer.

        Args:
            config (Config): Configuration object providing model access.
            base_prompt (str): Instructional prompt used to guide the model.

        """
        self.config = config
        self.base_prompt = base_prompt

    def score(
        self,
        task_data: list[str],
        metrics_to_score: list[Metric],
    ) -> list[Metric]:
        """Scores the given metrics based on the task data.

        Constructs a prompt using the base prompt, metrics, and task data,
        sends it to the model, and parses the structured response.

        Args:
            task_data (list[str]): Input data related to the task being evaluated.
            metrics_to_score (list[Metric]): The metrics to score using the model.

        Returns:
            list[Metric]: The scored metrics.

        """
        messages = [
            Message(role="user", content=self.base_prompt),
            Message(
                role="user",
                content="\n".join(
                    [
                        f"name={metric.name} description={metric.description}"
                        for metric in metrics_to_score
                    ]
                ),
            ),
            Message(role="user", content="\n".join(task_data)),
        ]

        metrics = (
            self.config.get_default_model().get_structured_response(messages, MetricList).metrics
        )
        [
            print(f"[LLM Judge] {metric.name}:{metric.score} explanation: {metric.explanation}")  # noqa: T201
            for metric in metrics
        ]

        return metrics
