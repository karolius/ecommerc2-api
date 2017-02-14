from rest_framework.pagination import LimitOffsetPagination


class ProductPagination(LimitOffsetPagination):
    default_limit = 1
    max_limit = 5
    limit_query_param = "limit"
    offset_query_param = "offset"
