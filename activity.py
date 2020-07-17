from model import Category, Location, District, Activity


def _get_item_by_name(cls, name):
    if name is not None:
        try:
            return cls.get(cls.name == name)
        except cls.DoesNotExist:
            return None
    return None


def query(**kwargs):
    category = _get_item_by_name(Category, kwargs.get('category', None))
    location = _get_item_by_name(Location, kwargs.get('location', None))
    district = _get_item_by_name(District, kwargs.get('district', None))

    q = Activity.select()
    if category:
        q = q.where(Activity.category == category)
    if location:
        q = q.where(Activity.location == location)
    if district:
        q = q.where(Activity.district == district)

    return {
        'type': 'FeatureCollection',
        'features': list(map(lambda act: act.geojson, q))
    }


def recommend():
    pass
