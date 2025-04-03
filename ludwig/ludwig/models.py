from django.db import models


class HarmData(models.Model):
    """
    Model representing necessary data for plotting harmonic values.
    
    Fields:
        harm_number (int): The harmonic number.
        p_harm_total (float): The total power for the harmonic.
        i_prevail_mag_1 (float): Phase A current magnitude.
        i_prevail_ang_1 (float): Phase A current angle.
        v_prevail_mag_1 (float): Phase A voltage magnitude.
        v_prevail_ang_1 (float): Phase A voltage angle.
        i_prevail_mag_2 (float): Phase B current magnitude.
        i_prevail_ang_2 (float): Phase B current angle.
        v_prevail_mag_2 (float): Phase B voltage magnitude.
        v_prevail_ang_2 (float): Phase B voltage angle.
        i_prevail_mag_3 (float): Phase C current magnitude.
        i_prevail_ang_3 (float): Phase C current angle.
        v_prevail_mag_3 (float): Phase C voltage magnitude.
        v_prevail_ang_3 (float): Phase C voltage angle.
    """
    harm_number = models.IntegerField(db_index=True)
    p_harm_total = models.FloatField()

    i_prevail_mag_1 = models.FloatField()
    i_prevail_ang_1 = models.FloatField()
    v_prevail_mag_1 = models.FloatField()
    v_prevail_ang_1 = models.FloatField()

    i_prevail_mag_2 = models.FloatField()
    i_prevail_ang_2 = models.FloatField()
    v_prevail_mag_2 = models.FloatField()
    v_prevail_ang_2 = models.FloatField()

    i_prevail_mag_3 = models.FloatField()
    i_prevail_ang_3 = models.FloatField()
    v_prevail_mag_3 = models.FloatField()
    v_prevail_ang_3 = models.FloatField()

    def __str__(self):
        return f"HarmData (HARM_NUMBER={self.harm_number})"
