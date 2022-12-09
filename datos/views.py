from django.http.response import JsonResponse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def nologin(request):
    try:
        if request.method == 'POST':
            #payload = json.loads(request.body)
            #id_medico = payload["id_medico"]
            nologin = User.objects.get(username="nologin")
            token = Token.objects.get(user_id=nologin.id)
            return JsonResponse({"token": token.key}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            return JsonResponse({'error':'Metodo no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except BaseException as e:
        msg = {'error': f'{str(e)}'}
        print("<nologin>", msg)
        return JsonResponse(msg, status=status.HTTP_400_BAD_REQUEST)                                
