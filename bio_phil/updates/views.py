from django.shortcuts import render
from .models import Updates
# Create your views here.

# View for the update model. 

# def updates(request):
#     Updates.object.order_by('-updates__id') #ordering by descending order by id number, test if it works, but if not then try using '-pub_date' instead
#     update_text = Updates.object.all()[0:4]
#     context = {'update_text':update_text}
#     return render(<insert html file name here pls ty =D>, context)

#use variable "update_text" is a python set, use python set slicing syntax to get to each element
# ex: a = update_text[0]
# print(a.update_text) #this will print out the latest update from the model.