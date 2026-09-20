from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, CommonMixin


class Feedback(Base, CommonMixin):
    __tablename__ = "feedback"

    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # POSITIVE, NEGATIVE
    rating: Mapped[str] = mapped_column(String(20), nullable=False)
    # INCORRECT_ANSWER, MISSING_INFO, WRONG_SOURCE, OUTDATED, OTHER
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
