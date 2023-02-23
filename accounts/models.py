from django.db import models
from back.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from items.models import Item
from assets.models import GameDate, Sector
from .managers import CustomUserManager

# Create your models here.

class User(AbstractUser):
   # 기본정보
   email = models.EmailField(_('email address'), unique=True)
   nickname = models.CharField(max_length=8, blank=True)
   refresh_token = models.TextField(blank=True)
   profile_img = models.TextField(blank=True) 
   username = None
   
   # 부가정보
   money = models.IntegerField(default=100000, blank=True)                       # 자산 (임시로 blank=True 해놓음)
   school = models.CharField(max_length=10, blank=True)
   # sector = models.ForeignKey(Sectors, on_delete=models.CASCADE)
      # 매수목록
   # position = models.ManyToManyField(Sectors, through=User_Positions)
   # 아이템 
   inventory = models.ManyToManyField(Item, through='User_Items')
   
   # 기능
   followers = models.ManyToManyField('self', symmetrical=True, related_name='following')    # Ture: 양방향 관계, 일촌 개념

   
   objects = CustomUserManager()
   
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = []

# 매수목록 ManyToManyField 확장
class User_Positions(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   position = models.ForeignKey(Sector, on_delete=models.CASCADE)
   day = models.ForeignKey(GameDate, on_delete=models.CASCADE)
   total = models.IntegerField(default=0)
   volume = models.IntegerField(default=0)

# 아이템목록(inventory) ManyToManyField 확장
class User_Items(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   item = models.ForeignKey(Item, on_delete=models.CASCADE)