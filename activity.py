import datetime

from flask import abort

from model import Category, Location, District, Activity, OpeningHour


def _get_item_by_name(cls, name):
    if name:
        try:
            return cls.get(cls.name == name.lower())
        except cls.DoesNotExist:
            return None
    return None


def query(**kwargs):
    q = Activity.select()

    if 'category' in kwargs:
        category = _get_item_by_name(Category, kwargs.get('category', None))
        q = q.where(Activity.category == category)
    if 'location' in kwargs:
        location = _get_item_by_name(Location, kwargs.get('location', None))
        q = q.where(Activity.location == location)
    if 'district' in kwargs:
        district = _get_item_by_name(District, kwargs.get('district', None))
        q = q.where(Activity.district == district)

    return {
        'type': 'FeatureCollection',
        'features': list(map(lambda act: act.geojson, q))
    }


def recommend(day, time, category):
    start, end = map(
        lambda x: datetime.datetime.strptime(x, '%H:%M'),
        time.split('-')
    )
    available_time = (start - end).total_seconds() / 3600
    start = start.time()
    end = end.time()
    category = _get_item_by_name(Category, category)

    q = Activity.select().join(OpeningHour).where(
        (Activity.category == category) &
        (OpeningHour.day == day) &
        # There's enough time to make the visit before it closes
        (
                (
                    # Interval starts after the activity has opened and there's enough time before the activity ends
                        (OpeningHour.start <= start) &
                        (start.hour + start.minute / 60 + Activity.hours_spent <=
                         OpeningHour.end.hour + OpeningHour.end.minute / 60)
                ) |
                (
                    # Activity opens after the free interval's start and there's enough time before the interval ends
                        (OpeningHour.start >= start) &
                        (OpeningHour.start.hour + OpeningHour.start.minute / 60 + Activity.hours_spent <=
                         end.hour + end.minute / 60)
                )
        )
    ).distinct().order_by(Activity.hours_spent.desc())

    if q.exists():
        return q[0].geojson
    return abort(404)
