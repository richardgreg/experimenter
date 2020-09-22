import random

import factory
from django.utils.text import slugify
from faker import Factory as FakerFactory

from experimenter.experiments.models import (
    NimbusBucketRange,
    NimbusExperiment,
    NimbusIsolationGroup,
)
from experimenter.openidc.tests.factories import UserFactory

faker = FakerFactory.create()


class NimbusExperimentFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda o: faker.catch_phrase())
    slug = factory.LazyAttribute(lambda o: "{}_".format(slugify(o.name)))
    public_description = factory.LazyAttribute(lambda o: faker.text(200))
    proposed_duration = factory.LazyAttribute(lambda o: random.randint(10, 60))
    proposed_enrollment = factory.LazyAttribute(
        lambda o: random.choice([None, random.randint(2, o.proposed_duration)])
        if o.proposed_duration
        else None
    )

    firefox_min_version = factory.LazyAttribute(
        lambda o: random.choice(NimbusExperiment.Version.choices)[0]
    )
    firefox_max_version = factory.LazyAttribute(
        lambda o: random.choice(NimbusExperiment.Version.choices)[0]
    )
    firefox_channel = factory.LazyAttribute(
        lambda o: random.choice(NimbusExperiment.Channel.choices)[0]
    )
    objectives = factory.LazyAttribute(lambda o: faker.text(1000))

    bugzilla_id = "12345"

    class Meta:
        model = NimbusExperiment

    @classmethod
    def create_with_status(cls, target_status, **kwargs):
        experiment = cls.create(**kwargs)

        for status, _ in NimbusExperiment.Status.choices:
            if status == NimbusExperiment.Status.REVIEW.value:
                NimbusIsolationGroup.request_isolation_group_buckets(
                    experiment.slug,
                    experiment,
                    100,
                )

            if status == target_status:
                break

        return NimbusExperiment.objects.get(id=experiment.id)


class NimbusIsolationGroupFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda o: slugify(faker.catch_phrase()))
    instance = factory.Sequence(lambda n: n)

    class Meta:
        model = NimbusIsolationGroup


class NimbusBucketRangeFactory(factory.django.DjangoModelFactory):
    experiment = factory.SubFactory(NimbusExperimentFactory)
    isolation_group = factory.SubFactory(NimbusIsolationGroupFactory)
    start = factory.Sequence(lambda n: n * 100)
    count = 100

    class Meta:
        model = NimbusBucketRange
