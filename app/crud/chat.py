from sqlalchemy.orm import Session

from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate


def get_chat_messages(db: Session, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .order_by(ChatMessage.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_chat_message(db: Session, message: ChatMessageCreate) -> ChatMessage:
    db_message = ChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
