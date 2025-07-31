from django.db import models

# =============================== Calendar =============================================


# EventType model: 이벤트 종류 및 색상 정의
class EventType(models.Model):
    """이벤트 종류 및 색상 정의"""
    name = models.CharField('event_type', max_length=20, unique=True)
    color = models.CharField('color', max_length=7, default='#3788d8',
                             help_text="HEX 코드 형식 예: #FF0000")

    def __str__(self):
        return self.name


class Calendar(models.Model):
    modal_title = models.CharField('calendar_name', default="휴진안내", help_text=r"줄넘기기 : \n", max_length=40)
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.modal_title


class Event(models.Model):
    title = models.CharField('title', default="휴진", max_length=20)
    date_of_event = models.DateField()
    calendar = models.ForeignKey(
        'Calendar',
        related_name='calendar',
        on_delete=models.PROTECT,
    )
    event_type = models.ForeignKey(
        'EventType',
        related_name='events',
        on_delete=models.PROTECT,
        null=True,  # ← 일단 null 허용
        blank=True,
    )

    def __str__(self):
        return str(self.title) + '/' + str(self.date_of_event)
