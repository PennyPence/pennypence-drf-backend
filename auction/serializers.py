from rest_framework import serializers
from .models import AuctionItem
from items.serializers import ItemSerializer
class AuctionItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = AuctionItem
        fields = '__all__'