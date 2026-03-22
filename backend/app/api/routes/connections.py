from fastapi import APIRouter

from app.models.schemas import ConnectionItem, ConnectionsResponse

router = APIRouter()


@router.get("/connections/{user_id}", response_model=ConnectionsResponse)
def list_connections(user_id: str) -> ConnectionsResponse:
    return ConnectionsResponse(
        user_id=user_id,
        connections=[
            ConnectionItem(
                connection_id="conn-2001",
                display_name="Avery",
                status="friend",
                voice_note_count=8,
                can_direct_call=True,
            ),
            ConnectionItem(
                connection_id="conn-2002",
                display_name="Jordan",
                status="matched",
                voice_note_count=3,
                can_direct_call=True,
            ),
        ],
    )
