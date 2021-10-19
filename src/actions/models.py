from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class Action(models.Model):
    user = models.ForeignKey('auth.User', related_name='actions', db_index=True, on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)

    '''
    Connecting the action's target object to be an instance of an existing model, done with 
    contenttypes framework. It tracks all models installed in the project and 
    provides a generic interface to interact with your models. To set up a generic relation in a model, 
    3 fields are needed: 1. Foreign key to ContentType, 2. a PositiveIntegerField to store the pk of the related model,
    and 3. a field to defina and manage the generic relation using the 2 previous fields.
    '''
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="targ_obj", on_delete=models.CASCADE)
    
    #for storing the primary key of the related object:
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    
    # field to the related object based on the combination of the two previous fields:
    target = GenericForeignKey('target_ct', "target_id")
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)
