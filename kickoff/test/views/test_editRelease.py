from datetime import datetime
from kickoff import app
from kickoff.model import FirefoxRelease
from base import ViewTest
import simplejson as json

class TestEditRelease(ViewTest):
	def testGetRelease(self):
		ret = self.get('/release/Firefox-2.0-build1/edit_release.html')
		self.assertEquals(ret.status_code, 200)

	def testGetReleaseWithError(self):
		ret = self.get('/release/Firefox-1/edit_release.html')
		self.assertEquals(ret.status_code, 404)

	def testEditRelease(self):
		release = {
			'shippedAtDate': '2013/03/03',
			'shippedAtTime': '14:44:00',
			'isSecurityDriven': True,
			'description': 'Edited Release!'
		}

		ret = self.post('/release/Firefox-2.0-build1/edit_release.html', data=release)

		with app.test_request_context():
			dbRelease = FirefoxRelease.query.filter_by(name='Firefox-2.0-build1').first()
			self.assertEquals(dbRelease.description, 'Edited Release!')
			self.assertTrue(dbRelease.isSecurityDriven)

			tm = datetime.strptime('14:44:00', '%H:%M:%S').time()
			dt = datetime(2013, 03, 03)

			dateAndTime = datetime.combine(dt, tm)
			self.assertEquals(dbRelease._shippedAt, dateAndTime)

	def testEditReleaseWithError(self):
		release = {
			'shippedAtDate': '2013/99/99',
			'shippedAtTime': '99:44:00',
			'isSecurityDriven': True,
			'description': 'Edited Release!'
		}

		ret = self.post('/release/Firefox-2.0-build1/edit_release.html', data=release)
		self.assertEquals(ret.status_code, 400)