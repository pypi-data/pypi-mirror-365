from django.db import models
from django.utils.translation import gettext_lazy as _


class Checklist(models.Model):
    class Category(models.TextChoices):
        INCIDENTAL = "Incidental", _("Incidental")
        STATIONARY = "Stationary", _("Stationary")
        TRAVELING = "Traveling", _("Traveling")
        AREA = "Area", _("Area")
        BANDING = "Banding", _("Banding")
        NOCTURNAL = "Nocturnal flight call Count", _("Nocturnal Flight Call Count")
        PELAGIC = "eBird Pelagic Protocol", _("eBird Pelagic Protocol")
        HISTORICAL = "Historical", _("Historical")

    class Protocol(models.TextChoices):
        INCIDENTAL = "P20",  _("Incidental")
        STATIONARY = "P21",  _("Stationary")
        TRAVELING = "P22", _("Traveling")
        AREA = "P23", _("Area")
        BANDING = "P33",  _("Banding")
        NOCTURNAL = "P54", _("Nocturnal Flight Call Count")
        PELAGIC = "P60", _("eBird Pelagic Protocol")
        HISTORICAL = "P62", _("Historical")
        STATIONARY_2_025 = "P67", _("Stationary (2-band, 25m)"),
        STATIONARY_2_030 = "P73", _("Stationary (2-band, 30m)"),
        STATIONARY_2_050 = "P88", _("Stationary (2-band, 50m)"),
        STATIONARY_2_075 = "P87", _("Stationary (2-band, 75m)"),
        STATIONARY_2_100 = "P89", _("Stationary (2-band, 100m)"),
        STATIONARY_3_030 = "P82", _("Stationary (3-band, 30m+100m)"),
        TRAVELING_2_025 = "P81", _("Traveling (2-band, 25m)"),
        DIRECTIONAL = "P68", _("Stationary (directional)"),

    class Meta:
        verbose_name = _("checklist")
        verbose_name_plural = _("checklists")

    identifier = models.CharField(
        max_length=15,
        primary_key=True,
        verbose_name=_("identifier"),
        help_text=_("The unique identifier for the checklist."),
    )

    edited = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("The date and time the eBird checklist was last edited."),
        verbose_name=_("edited"),
    )

    country = models.ForeignKey(
        "data.Country",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("country"),
        help_text=_("The country where the checklist was made."),
    )

    state = models.ForeignKey(
        "data.State",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("state"),
        help_text=_("The state where the checklist was made."),
    )

    county = models.ForeignKey(
        "data.County",
        blank=True,
        null=True,
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("county"),
        help_text=_("The county where the checklist was made."),
    )

    location = models.ForeignKey(
        "data.Location",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("location"),
        help_text=_("The location where checklist was made."),
    )

    observer = models.ForeignKey(
        "data.Observer",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("observer"),
        help_text=_("The person who submitted the checklist."),
    )

    group = models.TextField(
        blank=True,
        verbose_name=_("group"),
        help_text=_("The identifier for a group of observers."),
    )

    observer_count = models.IntegerField(
        default=0,
        verbose_name=_("observer count"),
        help_text=_("The total number of observers."),
    )

    species_count = models.IntegerField(
        default=0,
        verbose_name=_("species count"),
        help_text=_("The number of species reported."),
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

    observation_type = models.TextField(
        verbose_name=_("observation type"),
        help_text=_("The type of protocol followed."),
    )

    protocol_name = models.TextField(
        verbose_name=_("protocol name"),
        help_text=_("The name of protocol followed."),
    )

    protocol_code = models.CharField(
        max_length=3,
        db_index=True,
        verbose_name=_("protocol code"),
        help_text=_("The code used to identify the protocol."),
    )

    project_names = models.TextField(
        blank=True,
        verbose_name=_("project names"),
        help_text=_("The names used to identify the project (portal)."),
    )

    project_identifiers = models.TextField(
        blank=True,
        verbose_name=_("project identifiers"),
        help_text=_("The identifiers used for the project (portal)."),
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("duration"),
        help_text=_("The number of minutes spent counting."),
    )

    distance = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        verbose_name=_("distance"),
        help_text=_("The distance, in metres, covered while travelling."),
    )

    area = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        verbose_name=_("area"),
        help_text=_("The area covered, in hectares."),
    )

    complete = models.BooleanField(
        default=False,
        verbose_name=_("complete"),
        help_text=_("All species seen are reported."),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
        help_text=_("Any comments about the checklist."),
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When was the record created."),
    )

    modified = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When was the record modified."),
    )

    def __repr__(self) -> str:
        return str(self.identifier)

    def __str__(self) -> str:
        return str(self.identifier)
