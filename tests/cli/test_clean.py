from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseClean(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_clean(self):
        self.app = get_test_app(argv=['clean'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_clean_fastcgi(self):
        self.app = get_test_app(argv=['clean', '--fastcgi'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_clean_all(self):
        self.app = get_test_app(argv=['clean', '--all'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_clean_opcache(self):
        self.app = get_test_app(argv=['clean', '--opcache'])
        self.app.setup()
        self.app.run()
        self.app.close()
