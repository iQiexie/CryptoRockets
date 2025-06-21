import random
import traceback
from collections import defaultdict
from datetime import UTC
from datetime import datetime, timedelta
from typing import Annotated

import structlog
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types.payments import SavedStarGifts

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.config.constants import FUEL_CAPACITY_MAP
from app.config.constants import (
    ROCKET_CAPACITY_DEFAULT,
    ROCKET_CAPACITY_OFFLINE,
    ROCKET_CAPACITY_PREMIUM,
    ROCKET_TIMEOUT_DEFAULT,
    ROCKET_TIMEOUT_OFFLINE,
    ROCKET_TIMEOUT_PREMIUM,
)
from app.config.constants import TON_PRICE
from app.config.constants import WHEEL_TIMEOUT
from app.db.models import CurrenciesEnum, RocketTypeEnum, User
from app.db.models import Gift
from app.db.models import GiftStatusEnum
from app.db.models import GiftUserStatusEnum
from app.db.models import TransactionTypeEnum
from app.services.base.base import BaseService

logger = structlog.stdlib.get_logger()


class TaskService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.task
        self.adapters = adapters

    @BaseService.single_transaction
    async def _insert_gift(self, gift: dict) -> None:
        date = gift['date']
        slug, gift_id_ton = ([i.lower() for i in gift['gift']['slug'].split('-')])

        meta = dict()
        for attr in gift['gift']['attributes']:
            if not attr.get('name'):
                continue

            key = (
                attr['_']
                .replace('StarGiftAttribute', '')
                .lower()
            )

            value = {
                'name': attr['name'],
                'rarity': attr['rarity_permille'] / 1000,
            }

            meta[key] = value

        if not await self.repo.get_collection(slug=slug):
            await self.repo.create_collection(
                name=gift['gift']['title'],
                slug=slug,
                image=f"https://fragment.com/file/gifts/{slug.split('-')[0]}/thumb.webp",
                avg_price=None,
                meta={},
            )

        await self.repo.create_gift(
            collection_id=slug,
            transfer_date=date.astimezone(None).replace(tzinfo=None),
            address=gift['gift']['gift_address'],
            gift_id=str(gift['gift']['id']),
            gift_id_ton=gift_id_ton,
            status=GiftStatusEnum.available,
            image=f"https://nft.fragment.com/gift/{gift['gift']['slug']}.medium.jpg",
            meta=meta,
        )

    async def _populate_account_gifts(self) -> None:
        async with self.repo.transaction():
            last_gift = await self.repo.get_last_gift()

        async with TelegramClient(
            session='anon',
            api_id=5945038,
            api_hash='d9e26a347056c95b167ab097c73ec1f0',
        ) as client:
            result: SavedStarGifts = await client(
                functions.payments.GetSavedStarGiftsRequest(
                    peer='rockets_holder',  # noqa
                    offset='some_string',
                    limit=100000,
                    sort_by_value=False,
                )
            )

        gifts = result.to_dict()['gifts']

        if last_gift:
            last_date = last_gift.transfer_date
        else:
            last_date = datetime.now(tz=UTC) - timedelta(days=365)

        for gift in gifts:
            gift_date = gift['date'].astimezone(None).replace(tzinfo=None)
            last_date = last_date.astimezone(None).replace(tzinfo=None)
            if gift_date <= last_date:
                continue

            await self._insert_gift(gift=gift)

    async def _populate_shitty_gifts(self) -> None:
        gifts = await self.adapters.bot.get_available_gifts()
        for gift in gifts.gifts:
            gift_id = gift.id

            try:
                async with self.repo.transaction() as t:
                    await self.repo.create_collection(
                        name=gift.sticker.emoji,
                        slug=gift.sticker.emoji,
                        image=f"https://emojiapi.dev/api/v1/{ord(gift.sticker.emoji):X}.svg",
                        avg_price=(gift.star_count * 0.013) / TON_PRICE,
                        meta={"gift_id": gift_id},
                        is_nft=False,
                    )
                    await t.commit()
            except IntegrityError:
                pass

    async def populate_gifts(self) -> None:
        await self._populate_shitty_gifts()
        await self._populate_account_gifts()

    @BaseService.single_transaction
    async def give_rocket(self, rocket_type: RocketTypeEnum, full: bool, telegram_id: int) -> None:
        fuel_capacity = FUEL_CAPACITY_MAP.get(rocket_type, 1)

        await self.repos.user.create_user_rocket(
            type=rocket_type,
            user_id=telegram_id,
            fuel_capacity=fuel_capacity,
            current_fuel=fuel_capacity if full else 0,
        )

    async def grant_rocket(self, user: User) -> None:
        rockets_data = [
            dict(
                type=RocketTypeEnum.default,
                fuel_capacity=ROCKET_CAPACITY_DEFAULT,
                timeout=ROCKET_TIMEOUT_DEFAULT,
            ),
            dict(
                type=RocketTypeEnum.offline,
                fuel_capacity=ROCKET_CAPACITY_OFFLINE,
                timeout=ROCKET_TIMEOUT_OFFLINE,
            ),
            dict(
                type=RocketTypeEnum.premium,
                fuel_capacity=ROCKET_CAPACITY_PREMIUM,
                timeout=ROCKET_TIMEOUT_PREMIUM,
            ),
        ]

        existing_rockets = {rocket.type for rocket in user.rockets}

        if {i["type"].value for i in rockets_data}.issubset(existing_rockets):
            return

        given_rockets = list()

        async with self.repo.transaction() as t:
            for rocket in rockets_data:
                if rocket["type"].value in existing_rockets:
                    continue

                next_receive = getattr(user, f"next_{rocket['type'].value}_rocket_at")
                if next_receive > datetime.utcnow():
                    continue

                logger.info(f"Giving {rocket['type'].value} rocket to user {user.telegram_id}")

                await self.repos.user.create_user_rocket(
                    type=rocket["type"],
                    user_id=user.telegram_id,
                    fuel_capacity=rocket["fuel_capacity"],
                    current_fuel=0,
                )

                await self.repos.user.update_user(
                    **{
                        "telegram_id": user.telegram_id,
                        f"next_{rocket['type'].value}_rocket_at": datetime.utcnow() + timedelta(minutes=rocket["timeout"]),
                    }
                )

                given_rockets.append(rocket["type"].value)

            await t.commit()

        if RocketTypeEnum.premium in given_rockets:
            await self.adapters.bot.send_menu(
                user=user,
                custom_text=self.adapters.i18n.t("task.premium_rocket_given", user.tg_language_code),
                custom_image="https://3rioteam.fra1.cdn.digitaloceanspaces.com/ret2.jpg",
            )

    async def check_user_exists(self, telegram_id: int) -> bool:
        if await self.repos.user.get_user_by_telegram_id(telegram_id=telegram_id):
            return True

        return False

    async def give_offline_rocket(self) -> None:
        async with self.repo.transaction():
            users = await self.repo.get_offline_rocket_users()

        for user in users:
            try:
                await self.grant_rocket(user)
            except Exception as e:
                logger.error(
                    event=f"Failed to give offline rocket to user {user.telegram_id}: {e}",
                    exception=traceback.format_exception(e),
                )

    async def _give_wheel(self, user: User) -> None:
        async with self.repo.transaction() as t:
            await self.services.transaction.change_user_balance(
                telegram_id=user.telegram_id,
                currency=CurrenciesEnum.wheel,
                amount=1,
                user_kwargs=dict(next_wheel_at=datetime.utcnow() + timedelta(minutes=WHEEL_TIMEOUT)),
                tx_type=TransactionTypeEnum.retention
            )
            await t.commit()

    async def give_wheel(self) -> None:
        async with self.repo.transaction():
            users = await self.repo.get_wheel_users()

        for user in users:
            try:
                await self._give_wheel(user)
            except Exception as e:
                logger.error(
                    event=f"Failed to give wheel to user {user.telegram_id}: {e}",
                    exception=traceback.format_exception(e),
                )

    @staticmethod
    def _get_random_6_gifts(available_gifts: list[Gift]) -> list[Gift]:
        # Group available gifts by collection
        collection_to_gifts = defaultdict(list)
        for gift in available_gifts:
            collection_to_gifts[gift.collection_id].append(gift)

        # First, pick one random gift per unique collection (as many as possible)
        unique_collection_gifts = [random.choice(gifts) for gifts in collection_to_gifts.values()]
        random.shuffle(unique_collection_gifts)

        # If we have 6 or more unique collections, pick 6
        if len(unique_collection_gifts) >= 6:
            random_6_gifts = unique_collection_gifts[:6]
        else:
            # Otherwise, take all unique ones, and fill the rest randomly (duplicates allowed)
            needed = 6 - len(unique_collection_gifts)
            random_6_gifts = unique_collection_gifts + random.choices(available_gifts, k=needed)

        return random_6_gifts

    @BaseService.single_transaction
    async def populate_gifts_latest(self) -> None:
        blacklist_gifts = await self.repos.game.get_latest_gifts()
        available_gifts = await self.repo.get_fake_available_gifts(blacklist=[gift.id for gift in blacklist_gifts])
        random_6_gifts = self._get_random_6_gifts(available_gifts)

        for i,  gift in enumerate(random_6_gifts):
            try:
                await self.repos.game.create_gift_user(
                    user_id=388953283,
                    collection_id=gift.collection_id,
                    gift_id=gift.id,
                    roll_id=None,
                    status=GiftUserStatusEnum.created,
                    created_at=datetime.utcnow() + timedelta(seconds=i * 10),
                )
            except IntegrityError as e:
                await self.adapters.alerts.send_alert("populate_gifts_latest failed")
                logger.error(
                    event=f"Failed to create gift user for gift {gift.id}",
                    exception=traceback.format_exception(e),
                )
