from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        print(request.POST)  # or process incoming message
    return HttpResponse("Received", status=200)
