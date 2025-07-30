# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_handle_scan_error[single file exception] 1'] = '''Error: Scanning failed. Results may be incomplete.
Error: Add the following files to your ignored_paths:
Error: - /home/user/too/long/file/name: filename:: [ErrorDetail(string='Ensure this field has no more than 256 characters.', code='max_length')]
'''

snapshots['test_handle_scan_error[source not found] 1'] = '''Error: The provided source was not found in GitGuardian.
'''

snapshots['test_handle_scan_error[too many documents] 1'] = '''Error: Scanning failed. Results may be incomplete.
Error: The following chunk is affected:
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
- /example
Error: 400:Too many documents to scan
'''
