import json

from model import *


def create_tables():
    db.create_tables([Category, Location, City, District, Activity, OpeningHour])


def populate(city, file_path):
    city = City.create(name=city)

    with open(file_path) as file:
        activities = json.load(file)

        for act in activities:
            category, created = Category.get_or_create(name=act['category'])
            district, created = District.get_or_create(
                name=act['district'],
                city=city
            )
            location, created = Location.get_or_create(name=act['location'])

            activity = Activity.create(
                name=act['name'],
                hours_spent=act['hours_spent'],
                category=category,
                location=location,
                district=district,
                lat=act['latlng'][0],
                lng=act['latlng'][1]
            )

            for day in ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']:
                for interval in act['opening_hours'][day]:
                    start, end = interval.split('-')
                    OpeningHour.create(
                        activity=activity,
                        day=day,
                        start=start,
                        end=end
                    )


if __name__ == '__main__':
    create_tables()
    populate('madrid', 'madrid.json')
