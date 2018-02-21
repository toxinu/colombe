from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import BlockList


class BlockListResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'name': 'name',
        'country': 'country.code',
        'description': 'description',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'users': 'users',
    })

    def list(self):
        return BlockList.objects.all()

    def detail(self, pk):
        return BlockList.objects.get(id=pk)
