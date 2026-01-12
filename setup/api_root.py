# project/api_root.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            "clientes": reverse("clientes-list", request=request),
            "clientes-completo": reverse("cliente-list", request=request),
            "consumos": reverse("consumos-list", request=request),
        })
