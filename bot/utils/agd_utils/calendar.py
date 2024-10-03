import asyncio
import datetime
from datetime import date, timedelta
from typing import Dict, List

from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
    CalendarConfig,
    next_month_begin,
    get_today,
    empty_button,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    DATE_TEXT,
    TODAY_TEXT,
)
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.text import Text
from aiogram_i18n import I18nContext
from babel.dates import get_day_names, get_month_names


SELECTED_DAYS_KEY = "selected_dates"

calendar_config = CalendarConfig(
    min_date=datetime.date.today(),
)


class CalendarDaysViewCustom(CalendarDaysView):
    async def _render_days(
        self,
        config: CalendarConfig,
        offset: date,
        data: Dict,
        manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        dialog_data = manager.dialog_data
        keyboard = []
        # align beginning
        start_date = offset.replace(day=1)  # month beginning
        min_date = max(config.min_date, start_date)
        days_since_week_start = start_date.weekday() - config.firstweekday
        if days_since_week_start < 0:
            days_since_week_start += 7
        start_date -= timedelta(days=days_since_week_start)
        end_date = next_month_begin(offset) - timedelta(days=1)
        # align ending
        max_date = min(config.max_date, end_date)
        days_since_week_start = end_date.weekday() - config.firstweekday
        days_till_week_end = (6 - days_since_week_start) % 7
        end_date += timedelta(days=days_till_week_end)
        # add days
        today = get_today(config.timezone)
        for offset in range(0, (end_date - start_date).days, 7):
            row = []
            for row_offset in range(7):
                days_offset = timedelta(days=(offset + row_offset))
                current_date = start_date + days_offset
                if min_date <= current_date <= max_date:
                    row.append(
                        await self._render_date_button(
                            current_date,
                            today,
                            data,
                            manager,
                        )
                    )
                else:
                    row.append(empty_button())
            keyboard.append(row)
        return keyboard


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        locale = manager.middleware_data["i18n"].locale
        return get_day_names(
            width="short",
            context="stand-alone",
            locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: datetime.date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        i18n: I18nContext = manager.middleware_data["i18n"]
        locale = i18n.locale
        return get_month_names(
            "wide",
            context="stand-alone",
            locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysViewCustom(
                self._item_callback_data,
                date_text=MarkedDay("🔴", DATE_TEXT),
                today_text=MarkedDay("⭕", TODAY_TEXT),
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }
