"""Note endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.note_service import NoteService

router = APIRouter()


@router.post("/days/{day_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    day_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new note for a day.

    Args:
        day_id: Day ID to associate note with
        note_data: Note creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        NoteResponse with status 201

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # First check if day exists
    day = db.query(Day).filter(Day.id == day_id).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    # Verify day belongs to current user
    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add notes to this day",
        )

    # Create note (exclude day_id from note_data as we use path parameter)
    note_dict = note_data.model_dump(exclude={"day_id"})

    try:
        note = NoteService.create_note(db, day_id, note_dict)
        return note
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/days/{day_id}/notes", response_model=List[NoteResponse])
def get_notes_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notes for a specific day.

    Args:
        day_id: Day ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of notes ordered by created_at desc

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # First check if day exists
    day = db.query(Day).filter(Day.id == day_id).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    # Verify day belongs to current user
    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view notes for this day",
        )

    notes = NoteService.get_notes_by_day(db, day_id)
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific note by ID.

    Args:
        note_id: Note ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Note data

    Raises:
        HTTPException: 404 if note not found, 403 if not authorized
    """
    note = NoteService.get_note(db, note_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Verify note's day belongs to current user
    if note.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this note",
        )

    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update note information.

    Args:
        note_id: Note ID to update
        note_data: Note update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated note data

    Raises:
        HTTPException: 404 if note not found, 403 if not authorized
    """
    # First check if note exists
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Verify note's day belongs to current user
    if note.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this note",
        )

    # Update note with only the fields that are provided
    update_data = note_data.model_dump(exclude_unset=True)

    try:
        updated_note = NoteService.update_note(db, note_id, **update_data)
        return updated_note
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete note.

    Args:
        note_id: Note ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if note not found, 403 if not authorized
    """
    # First check if note exists
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Verify note's day belongs to current user
    if note.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note",
        )

    # Delete note
    success = NoteService.delete_note(db, note_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    return None
