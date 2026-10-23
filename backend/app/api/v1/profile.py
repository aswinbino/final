"""
User Profile API
POST /api/v1/profile
GET  /api/v1/profile/{profile_id}
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import UserProfile
from app.schemas.contract import UserProfileCreate, UserProfileResponse

router = APIRouter()


@router.post("", response_model=UserProfileResponse, summary="Create user profile")
async def create_profile(data: UserProfileCreate, db: AsyncSession = Depends(get_db)):
    """Create a user profile for personalized risk analysis."""
    profile = UserProfile(name=data.name, role=data.role, preferences=data.preferences)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=UserProfileResponse, summary="Get user profile")
async def get_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).where(UserProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found.")
    return profile
