from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Observation(models.Model):
    class BreedingCode(models.TextChoices):
        NEST_WITH_YOUNG = "NY", _("Nest with young")
        NEST_WIH_EGGS = "NE", _("Nest containing eggs")
        FECAL_SAC = "FS", _("Adult carrying a faecal sac")
        FEEDING_YOUNG = "FY", _("Adult feeding young")
        CARRYING_FOOD = "CF", _("Adult carrying food")
        RECENTLY_FLEDGED = "FL", _("Recently fledged young")
        OCCUPIED_NEST = "ON", _("Occupied nest")
        USED_NEST = "UN", _("Used nest")
        DISTRACTION_DISPLAY = "DD", _("Distraction display")
        NEST_BUILDING = "NB", _("Nest-building")
        CARRYING_MATERIAL = "CN", _("Carrying nest material")
        BROOD_PATCH = "PE", _("Brood patch")
        APPARENT_NEST = "B", _("Woodpecker or Wren nest-building")
        AGITATED_BEHAVIOUR = "A", _("Agitated behaviour")
        NEST_VISITED = "N", _("Nest-site visited")
        COURTSHIP = "C", _("Courtship, display, or copulation")
        TERRITORY = "T", _("Territorial defense")
        PAIR = "P", _("Pair in suitable habitat")
        MULTIPLE_SINGING = "M", _("Multiple singing males")
        MULTIPLE_DAYS = "S7", _("Male singing for multiple days")
        SINGING = "S", _("Singing male")
        HABITAT = "H", _("Adult in suitable habitat")
        FLYOVER = "FO", _("Fly-over")

    class BreedingCategory(models.TextChoices):
        OBSERVED = "C1", _("Bird observed")
        POSSIBLE = "C2", _("Breeding possible")
        PROBABLE = "C3", _("Breeding probable")
        CONFIRMED = "C4", _("Breeding confirmed")

    class Age(models.TextChoices):
        ADULT = "adult", _("Adult")
        IMMATURE = "immature", _("Immature")
        JUVENILE = "juvenile", _("Juvenile")

    class Sex(models.TextChoices):
        FEMALE = "femail", _("Female")
        MALE = "male", _("Male")
        UNKNOWN = "unknown", _("Sex unknown")

    class Meta:
        verbose_name = _("observation")
        verbose_name_plural = _("observations")

    identifier = models.CharField(
        max_length=15,
        primary_key=True,
        verbose_name=_("identifier"),
        help_text=_("The identifier for the observation."),
    )

    edited = models.DateTimeField(
        help_text=_("The date and time the observation was last edited"),
        verbose_name=_("edited"),
    )

    checklist = models.ForeignKey(
        "data.Checklist",
        related_name="observations",
        on_delete=models.CASCADE,
        verbose_name=_("checklist"),
        help_text=_("The checklist this observation belongs to."),
    )

    species = models.ForeignKey(
        "data.Species",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("species"),
        help_text=_("The identified species."),
    )

    observer = models.ForeignKey(
        "data.Observer",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("observer"),
        help_text=_("The person who made the observation."),
    )

    country = models.ForeignKey(
        "data.Country",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("country"),
        help_text=_("The country where the observation was made."),
    )

    state = models.ForeignKey(
        "data.State",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("state"),
        help_text=_("The state where the observation was made."),
    )

    county = models.ForeignKey(
        "data.County",
        blank=True,
        null=True,
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("county"),
        help_text=_("The county where the observation was made."),
    )

    location = models.ForeignKey(
        "data.Location",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("location"),
        help_text=_("The location where the observation was made."),
    )

    date = models.DateField(
        db_index=True,
        verbose_name=_("date"),
        help_text=_("The date the observations were made."),
    )

    time = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_("time"),
        help_text=_("The time the observations were made."),
    )

    started = models.DateTimeField(
        blank=True,
        db_index=True,
        null=True,
        verbose_name=_("date & time"),
        help_text=_("The date and time the observations were made."),
    )

    count = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_("count"),
        help_text=_("The number of birds seen."),
    )

    breeding_code = models.CharField(
        max_length=2,
        blank=True,
        db_index=True,
        verbose_name=_("breeding code"),
        help_text=_("eBird code identifying the breeding status."),
    )

    breeding_category = models.CharField(
        max_length=2,
        blank=True,
        db_index=True,
        verbose_name=_("breeding category"),
        help_text=_("eBird code identifying the breeding category."),
    )

    behavior_code = models.CharField(
        max_length=2,
        blank=True,
        db_index=True,
        verbose_name=_("behaviour code"),
        help_text=_("eBird code identifying the behaviour."),
    )

    age_sex = models.TextField(
        blank=True,
        verbose_name=_("Age & Sex"),
        help_text=_("The number of birds seen in each combination of age and sex."),
    )

    media = models.BooleanField(
        verbose_name=_("has media"),
        help_text=_("Has audio, photo or video uploaded to the Macaulay library."),
    )

    approved = models.BooleanField(
        verbose_name=_("Approved"),
        help_text=_("Has the observation been accepted by eBird's review process."),
    )

    reviewed = models.BooleanField(
        verbose_name=_("Reviewed"),
        help_text=_("Was the observation reviewed because it failed automatic checks."),
    )

    reason = models.TextField(
        blank=True,
        verbose_name=_("Reason"),
        help_text=_(
            "The reason given for the observation to be marked as not confirmed."
        ),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
        help_text=_("Any comments about the observation."),
    )

    urn = models.TextField(
        blank=True,
        verbose_name=_("URN"),
        help_text=_("The globally unique identifier for the observation."),
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text=_("When was the record created."),
    )

    modified = models.DateTimeField(
        auto_now=True, help_text=_("When was the record updated.")
    )

    def __repr__(self) -> str:
        return str(self.identifier)

    def __str__(self) -> str:
        return str(self.identifier)
