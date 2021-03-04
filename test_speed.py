
import os
import tempfile

import pytest

from speed import create_app


@pytest.fixture
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    # create_app.config['TESTING'] = True

    client = create_app.app.test_client()
    return client

#     with flaskr.app.test_client() as client:
#         with flaskr.app.app_context():
#             flaskr.init_db()
#         yield client

#     os.close(db_fd)
#     os.unlink(flaskr.app.config['DATABASE'])

def test_location_list(client):

    response = client.get('/location_list')
    assert response.status_code == 200