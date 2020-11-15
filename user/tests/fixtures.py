from datetime import datetime

import factory

from user.models import UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    date_joined = factory.LazyFunction(datetime.now)
    password = factory.PostGenerationMethodCall('set_password', '12345')
