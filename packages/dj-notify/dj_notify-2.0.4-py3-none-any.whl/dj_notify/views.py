from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        print(request.POST)  # or process incoming message
    return HttpResponse("Received", status=200)

@csrf_exempt
def email_reply_webhook(request):
    if request.method == "POST":
        sender = request.POST.get("sender")
        subject = request.POST.get("subject")
        body_plain = request.POST.get("body-plain")

        NotificationLog.objects.create(
            sent_to=sender,
            message=body_plain,
            notification_type="email",
            status="sent"
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid"}, status=400)