from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.db import IntegrityError
from ..providers import esi

from django.db import models
from allianceauth.eveonline.models import EveCharacter

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

class TaxLedger(models.Model):
    corporation_id = models.BigIntegerField()
    alliance_id = models.BigIntegerField()
    journal_reference_id = models.BigIntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    taxed_amount = models.DecimalField(max_digits=20, decimal_places=2)
    ref_type = models.CharField(max_length=100)
    date = models.DateTimeField()
    generated_by = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["corporation_id", "journal_reference_id"], name="pk_taxledger")
        ]
        indexes = [
            models.Index(fields=["date"]),
        ]
    
    def __str__(self):
        return f"{self.generated_by} - {self.date.date()} - {self.amount} ISK - {self.ref_type}"
    
    @classmethod
    def import_from_corp_ledger(cls, corporation_ledger: list, corporation_id: int, alliance_tax_rate: float):

        character_ids = list({int(entry.generated_by) for entry in corporation_ledger})

        character_mapping = {
            entry["id"]: entry["name"]
            for entry in esi.client.Universe.post_universe_names(ids=character_ids).results()
        }

        corporation_data = esi.client.Corporation.get_corporations_corporation_id(
            corporation_id=corporation_id
        ).results()
        corporation_tax_rate = round(corporation_data["tax_rate"]*100, 2)
        current_alliance_id = corporation_data["alliance_id"]
        
        logger.info(f"Adding/Updating all the entries for the corporation tax")
        for entry in corporation_ledger:
            try:
                cls.objects.update_or_create(
                    corporation_id=corporation_id,
                    journal_reference_id=entry.id,
                    amount=entry.amount,
                    taxed_amount=entry.amount * (Decimal(str(alliance_tax_rate))/Decimal(str(corporation_tax_rate))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                    ref_type=entry.ref_type,
                    date=entry.date,
                    generated_by=character_mapping.get(entry.generated_by),
                    alliance_id=current_alliance_id
                )
            except IntegrityError as e:
                logger.warning(f"Ledger entry {entry.id} failed (integrity error): {e}")
            except Exception as e:
                logger.exception(f"Ledger entry {entry.id} failed with error: {e}")