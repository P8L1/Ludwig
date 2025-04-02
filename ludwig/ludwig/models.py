from django.db import models


class HarmonicRecord(models.Model):
    harmonic_number = models.IntegerField(db_index=True)
    v_prevail_ang1 = models.FloatField(null=True, blank=True)
    v_prevail_ang2 = models.FloatField(null=True, blank=True)
    v_prevail_ang3 = models.FloatField(null=True, blank=True)
    v_prevail_ang4 = models.FloatField(null=True, blank=True)
    v_prevail_mag1 = models.FloatField(null=True, blank=True)
    v_prevail_mag2 = models.FloatField(null=True, blank=True)
    v_prevail_mag3 = models.FloatField(null=True, blank=True)
    v_prevail_mag4 = models.FloatField(null=True, blank=True)
    I_prevail_ang1 = models.FloatField(null=True, blank=True)
    I_prevail_ang2 = models.FloatField(null=True, blank=True)
    I_prevail_ang3 = models.FloatField(null=True, blank=True)
    I_prevail_ang4 = models.FloatField(null=True, blank=True)
    I_prevail_mag1 = models.FloatField(null=True, blank=True)
    I_prevail_mag2 = models.FloatField(null=True, blank=True)
    I_prevail_mag3 = models.FloatField(null=True, blank=True)
    I_prevail_mag4 = models.FloatField(null=True, blank=True)

    def __str__(self):
        # Assert that harmonic_number is a valid integer before using it in the string.
        assert isinstance(self.harmonic_number, int), "harmonic_number must be an integer"
        return f"HarmonicRecord({self.harmonic_number})"
