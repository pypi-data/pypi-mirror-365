from django.db import models
from django.utils.translation import gettext_lazy as _


class Observer(models.Model):
    class Meta:
        verbose_name = _("observer")
        verbose_name_plural = _("observers")

    identifier = models.CharField(
        max_length=15,
        primary_key=True,
        verbose_name=_("identifier"),
        help_text=_("The identifier for the person submitted the checklist."),
    )

    orcid = models.TextField(
        blank=True,
        verbose_name=_("ORCID Identifier"),
        help_text=_("The observer's ORCID Identifier, see https://orcid.org/."),
    )

    name = models.TextField(
        blank=True,
        verbose_name=_("name"),
        help_text=_("The observer's name."),
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text=_("When was the record created."),
    )

    modified = models.DateTimeField(
        auto_now=True, help_text=_("When was the record updated.")
    )

    def __repr__(self):
        return str(self.identifier)

    def __str__(self):
        return str(self.name or self.identifier)
