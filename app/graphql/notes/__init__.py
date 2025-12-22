"""Notes module for CRM system."""

from app.graphql.notes.mutations import NotesMutations
from app.graphql.notes.queries import NotesQueries
from app.graphql.notes.repositories import (
    NoteConversationsRepository,
    NotesRepository,
)
from app.graphql.notes.services import NotesService
from app.graphql.notes.strawberry import (
    NoteConversationInput,
    NoteConversationType,
    NoteInput,
    NoteType,
)

__all__ = [
    "NotesRepository",
    "NoteConversationsRepository",
    "NotesService",
    "NoteInput",
    "NoteConversationInput",
    "NoteType",
    "NoteConversationType",
    "NotesMutations",
    "NotesQueries",
]
