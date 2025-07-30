from rest_framework.test import APITestCase


class ES_index_exists( APITestCase ):
    model = None

    def test_index_exists( self ):
        index_exists = self.model._index.exists()
        self.assertTrue( index_exists )
