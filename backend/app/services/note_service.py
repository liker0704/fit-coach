"""Note service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.note import Note


class NoteService:
    """Service for note operations."""

    @staticmethod
    def create_note(db: Session, day_id: int, note_data: dict) -> Note:
        """Create new note for a day.

        Args:
            db: Database session
            day_id: Day ID to associate note with
            note_data: Dictionary containing note fields

        Returns:
            Newly created Note object

        Raises:
            ValueError: If required fields are missing
        """
        if "content" not in note_data:
            raise ValueError("Note content is required")

        new_note = Note(day_id=day_id, **note_data)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note

    @staticmethod
    def get_note(db: Session, note_id: int) -> Optional[Note]:
        """Get note by ID.

        Args:
            db: Database session
            note_id: Note ID

        Returns:
            Note object or None if not found
        """
        return db.query(Note).filter(Note.id == note_id).first()

    @staticmethod
    def get_notes_by_day(db: Session, day_id: int) -> List[Note]:
        """Get all notes for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of Note objects ordered by created_at desc
        """
        return (
            db.query(Note)
            .filter(Note.day_id == day_id)
            .order_by(Note.created_at.desc())
            .all()
        )

    @staticmethod
    def update_note(db: Session, note_id: int, **kwargs) -> Note:
        """Update note with field validation.

        Args:
            db: Database session
            note_id: Note ID
            **kwargs: Fields to update (title, content, tags, attachments)

        Returns:
            Updated Note object

        Raises:
            ValueError: If note not found
        """
        note = db.query(Note).filter(Note.id == note_id).first()

        if not note:
            raise ValueError(f"Note with id {note_id} not found")

        # Update allowed fields
        allowed_fields = {
            "title",
            "content",
            "tags",
            "attachments",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(note, field, value)

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete_note(db: Session, note_id: int) -> bool:
        """Delete note.

        Args:
            db: Database session
            note_id: Note ID

        Returns:
            True if deleted, False if not found
        """
        note = db.query(Note).filter(Note.id == note_id).first()

        if not note:
            return False

        db.delete(note)
        db.commit()
        return True
