import factory

from clubs.models import Club


class ClubFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Club

    name = "Test"
    post_code = 33100
    latitude = 35.0
    longitude = 47.0
