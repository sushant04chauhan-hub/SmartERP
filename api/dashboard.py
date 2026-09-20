from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.dashboard_data import (
    build_dashboard_data,
)


class DashboardAPIView(APIView):

    def get(self, request):

        return Response(
            build_dashboard_data()
        )