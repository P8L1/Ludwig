from rest_framework import serializers
from .models import HarmData


class HarmDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the HarmData model.
    Serializes all necessary fields for plotting.
    """
    class Meta:
        model = HarmData
        fields = [
            'id',
            'harm_number',
            'p_harm_total',
            'i_prevail_mag_1', 'i_prevail_ang_1', 'v_prevail_mag_1', 'v_prevail_ang_1',
            'i_prevail_mag_2', 'i_prevail_ang_2', 'v_prevail_mag_2', 'v_prevail_ang_2',
            'i_prevail_mag_3', 'i_prevail_ang_3', 'v_prevail_mag_3', 'v_prevail_ang_3'
        ]
