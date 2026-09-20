from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, CommonMixin, utc_now


class EvaluationDataset(Base, CommonMixin):
    __tablename__ = "evaluation_datasets"

    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)


class EvaluationQuestion(Base, CommonMixin):
    __tablename__ = "evaluation_questions"

    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_datasets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_topic: Mapped[str] = mapped_column(String(255), default="", nullable=False)


class EvaluationRun(Base, CommonMixin):
    __tablename__ = "evaluation_runs"

    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_datasets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # PENDING, RUNNING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    metrics_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    latency_avg_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    failure_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
