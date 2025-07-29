from django.db import models
from django.utils.translation import gettext_lazy as _


class Species(models.Model):
    class Category(models.TextChoices):
        SPECIES = "species", _("Species")
        SLASH = "slash", _("Species pairs")
        SUBSPECIES = "issf", _("Subspecies")
        DOMESTIC = "domestic", _("Domestic species")
        HYBRID = "hybrid", _("Hybrids")
        FORM = "form", _("Species forms")
        SPUH = "spuh", _("Unidentified species")
        INTERGRADE = "intergrade", _("Intergrades")

    class Exotic(models.TextChoices):
        NATURALIZED = "N", _("Naturalized")
        PROVISIONAL = "P", _("Provisional")
        ESCAPEE = "X", _("Escapee")

    class Meta:
        verbose_name = _("species")
        verbose_name_plural = _("species")

    order = models.IntegerField(
        db_index=True,
        verbose_name=_("taxonomic order"),
        help_text=_("The position in the eBird/Clements taxonomic order."),
    )

    category = models.TextField(
        choices=Category,
        db_index=True,
        verbose_name=_("category"),
        help_text=_("The category from the eBird/Clements taxonomy."),
    )

    concept = models.TextField(
        verbose_name=_("Taxonomic Concept Identifier"),
        help_text=_("The Avibase identifier for the species."),
    )

    common_name = models.TextField(
        verbose_name=_("common name"),
        help_text=_("The species common name in the eBird/Clements taxonomy."),
    )

    scientific_name = models.TextField(
        verbose_name=_("scientific name"),
        help_text=_("The species scientific name in the eBird/Clements taxonomy."),
    )

    subspecies_common_name = models.TextField(
        blank=True,
        verbose_name=_("subspecies common name"),
        help_text=_(
            "The subspecies, group or form common name in the eBird/Clements taxonomy."
        ),
    )

    subspecies_scientific_name = models.TextField(
        blank=True,
        verbose_name=_("Scientific name"),
        help_text=_(
            "The subspecies, group or form scientific name in the eBird/Clements taxonomy."
        ),
    )

    exotic_code = models.TextField(
        blank=True,
        db_index=True,
        verbose_name=_("exotic code"),
        help_text=_("The code used if the species is non-native."),
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text=_("When was the record created."),
    )

    modified = models.DateTimeField(
        auto_now=True, help_text=_("When was the record updated.")
    )

    def __repr__(self) -> str:
        return str(self.order)

    def __str__(self):
        return str(self.subspecies_common_name or self.common_name)
