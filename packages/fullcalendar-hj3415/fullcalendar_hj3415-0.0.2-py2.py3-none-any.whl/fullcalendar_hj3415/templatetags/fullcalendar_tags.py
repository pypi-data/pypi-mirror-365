# ================================== calendar ====================================
from datetime import datetime, timedelta
from django import template

from ..models import Calendar, Event

register = template.Library()

@register.inclusion_tag(f"fullcalendar_hj3415/_load.html")
def show_calendar():
    try:
        # 활성화된 달력에서 하나(제일 처음 것)을 선택함.
        calendar1 = Calendar.objects.filter(activate__exact=True)[0]
    except IndexError:
        calendar1 = None

    try:
        # 달력의 이벤트 날짜들을 저장함.
        events = Event.objects.filter(calendar__exact=calendar1)
    except IndexError:
        events = None

    print(events)
    context = {
        "dont_show_again": "다시보지않기",
        "calendar": calendar1,
        "events": events,
        "default_date": set_default_date().strftime("%Y-%m-%d"),
    }
    print("calendards context: ", context)
    return context


def set_default_date(date=25) -> datetime:
    """
    full calendar의 defaultDate를 설정하는 함수
    date 인자 이후의 날짜는 다음달을 표시하도록 default day를 다음달로 반환한다.
    """
    today = datetime.today()
    if today.day >= date:
        return today + timedelta(days=7)
    else:
        return today