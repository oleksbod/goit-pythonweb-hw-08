from datetime import date, timedelta

from sqlalchemy import func
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import extract, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> List[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id)

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int
    ) -> List[Contact]:
        stmt = (
            select(Contact)
            .filter(
                Contact.first_name.ilike(f"%{search}%")
                | Contact.last_name.ilike(f"%{search}%")
                | Contact.email.ilike(f"%{search}%")
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_birthdays(self, days: int) -> List[Contact]:
        today = date.today()
        future_date = today + timedelta(days=days)

        stmt = select(Contact).filter(Contact.birthday.isnot(None))

        if today.month == future_date.month:
            stmt = stmt.filter(
                extract("month", Contact.birthday) == today.month,
                extract("day", Contact.birthday).between(today.day, future_date.day),
            )
        else:
            # Діапазон охоплює два місяці (перехід через новий рік)
            stmt = stmt.filter(
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == future_date.month,
                        extract("day", Contact.birthday) <= future_date.day,
                    ),
                )
            )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
