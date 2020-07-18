from peewee import *

db = SqliteDatabase('cartotest.db')


class Category(Model):
    name = CharField()

    class Meta:
        database = db


class Location(Model):
    name = CharField()

    class Meta:
        database = db


class City(Model):
    name = CharField()

    class Meta:
        database = db


class District(Model):
    name = CharField()
    city = ForeignKeyField(City, backref='districts')

    class Meta:
        database = db


class Activity(Model):
    name = CharField()
    hours_spent = FloatField()
    category = ForeignKeyField(Category, backref='activities')
    location = ForeignKeyField(Location, backref='activities')
    district = ForeignKeyField(District, backref='activities')
    lat = FloatField()
    lng = FloatField()

    def _get_opening_hours_json(self):
        result = {}
        for day in ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']:
            intervals = []
            for oh in self.opening_hours.where(OpeningInterval.day == day).order_by(OpeningInterval.start):
                intervals.append(f'{oh.start}-{oh.end}')
            result[day] = intervals
        return result

    @property
    def geojson(self):
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lng, self.lat]
            },
            'properties': {
                'name': self.name,
                'opening_hours': self._get_opening_hours_json(),
                'hours_spent': self.hours_spent,
                'category': self.category.name,
                'location': self.location.name,
                'district': self.district.name
            }
        }

    class Meta:
        database = db


class OpeningInterval(Model):
    activity = ForeignKeyField(Activity, backref='opening_hours')
    day = CharField()
    start = TimeField()
    end = TimeField()

    class Meta:
        database = db
