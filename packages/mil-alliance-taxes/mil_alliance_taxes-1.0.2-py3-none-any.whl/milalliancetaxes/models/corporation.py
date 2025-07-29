from decimal import Decimal
from django.db import models
from django.db.models import Sum

from ..providers import esi

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

from ..app_settings import (
    MILALLIANCETAXES_ALLIANCE_ID
)

class Corporation(models.Model):
    corporation_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    is_updated = models.BooleanField(default=False)

    def get_tax_for_month(self, year: int, month: int) -> Decimal:
        from .tax_ledger import TaxLedger

        entries_for_month = TaxLedger.objects.filter(
            corporation_id=self.corporation_id,
            date__year=year,
            date__month=month,
            alliance_id=MILALLIANCETAXES_ALLIANCE_ID
        )

        logger.info(f"{entries_for_month.count()} entries retrieved from the ledger for the corporation {self.corporation_id} - month {month} - year {year}")

        return entries_for_month.aggregate(total_amount=Sum('taxed_amount'))['total_amount'] or Decimal('0.00')
    
    @staticmethod
    def create_missing_corporation(corporation_id: int):
        corporation_data = esi.client.Corporation.get_corporations_corporation_id(
            corporation_id=corporation_id
        ).results()

        corporation, _ = Corporation.objects.update_or_create(
            corporation_id=corporation_id,
            defaults={
                "name": corporation_data["name"],
                "is_updated": False
            }
        )

        return corporation