import datetime

import pytz
from flask import abort

from model import Category, Location, District, Activity, OpeningInterval, WEEK_DAYS


def _get_item_by_name(cls, name):
    """
    Gets the item from the corresponding class with the indicated name.
    :param cls: Class / Entity of the item.
    :param name: Case-insensitive name of the item.
    :return: The item if there is a match, None otherwise.
    """
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


def recommend(time, category):
    day = datetime.datetime.now(pytz.timezone('Europe/Madrid'))  # TODO Get the specific city timezone
    day = WEEK_DAYS[day.weekday()]
    start, end = map(
        lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
        time.split('-')
    )
    category = _get_item_by_name(Category, category)

    # User's interval bounds expressed in hours
    user_start_hour = start.hour + start.minute / 60
    user_end_hour = end.hour + end.minute / 60

    # Activities opening intervals bounds expressed in hours
    activity_start_hour = OpeningInterval.start.hour + OpeningInterval.start.minute / 60
    activity_end_hour = OpeningInterval.end.hour + OpeningInterval.end.minute / 60

    q = Activity.select().join(OpeningInterval).where(
        (Activity.category == category) &
        (OpeningInterval.day == day) &
        # There's enough time to make the visit before it closes
        (
                (
                    # Activity start <= user interval start
                        (OpeningInterval.start <= start) &
                        (user_start_hour + Activity.hours_spent <= activity_end_hour) &
                        (user_start_hour + Activity.hours_spent <= user_end_hour)
                ) |
                (
                    # Activity start >= user interval start
                        (OpeningInterval.start >= start) &
                        (activity_start_hour + Activity.hours_spent <= user_end_hour)
                )
        )
    ).order_by(Activity.hours_spent.desc())

    if q.exists():
        return q[0].geojson
    return abort(404)
