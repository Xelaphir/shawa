from rest_framework.pagination import PageNumberPagination


class LotsPg(PageNumberPagination):
    page_size = 20
