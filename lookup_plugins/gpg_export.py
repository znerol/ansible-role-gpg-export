from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: gpg_export
    author: Lorenz Schori <lo@znerol.ch>
    short_description: export gpg public key
    description:
      - Export a GPG public key from a keyring on the controller
    options:
      _uids:
        description: gpg uid
        required: True
      executable:
        description: full path to the gpg binary
        type: string
        required: False
        default: >
            /usr/bin/gpg (Ansible < 2.7) or located automatically in PATH
            environment variable (Ansible >= 2.7).
      homedir:
        description: path to the gnupg home directory (see man 1 gpg)
        type: string
        required: False
        default: ~/.gnupg
      armor:
        description: produce ASCII armored output (see man 1 gpg)
        type: boolean
        required: False
        default: True
      export_options:
        description: options for the exported keys (see man 1 gpg)
        type: list
        required: False
        default: []
      match:
        description: >
            one of 'default', 'exact_uid', 'exact_email', 'partial_email',
            'keygrip' specifying how keys are matched to the given uids. (see
            man 1 gpg)
        type: string
        required: False
        default: default
    notes:
      - Like all lookups this runs on the Ansible controller and is unaffected
        by other keywords, such as become, so if you need to different
        permissions you must change the command or run Ansible as another user.
"""

EXAMPLES = """
- name: Publish armored GPG public key on webserver
  copy:
    content: "{{ lookup('gpg_export', 'test@example.com', armor=True, match='exact_uid') }}"
    dest: /var/www/my-key.asc
"""

RETURN = """
  _string:
    description:
      - exported gpg public key
"""

import codecs
import subprocess

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text
from ansible.plugins.lookup import LookupBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

# Ansible to_text function uses the 'surrogateescape' error handler if it is
# available. This will preserve any binary data until it is encoded / written
# to disk again. This error handler was introduced in Python 3.1.
#
# See also:
# * https://docs.python.org/3/library/codecs.html?highlight=surrogateescape#codec-base-classes
# * https://www.python.org/dev/peps/pep-0383/
try:
    codecs.lookup_error('surrogateescape')
    HAS_SURROGATEESCAPE = True
except LookupError:
    HAS_SURROGATEESCAPE = False

try:
    from ansible.module_utils.common.process import get_bin_path
    HAS_BINPATH = True
except ImportError:
    HAS_BINPATH = False

class LookupModule(LookupBase):

    def run(self, uids, variables, **kwargs):
        args = []

        if HAS_BINPATH:
            executable = kwargs.get('executable', 'gpg')
            if '/' not in executable and HAS_BINPATH:
                executable = get_bin_path(executable)
        else:
            executable = kwargs.get('executable', '/usr/bin/gpg')

        args.append(executable)

        homedir = kwargs.get('homedir', None)
        if homedir is not None:
            args.extend(['--homedir', homedir])

        armor = kwargs.get('armor', True)
        if armor is True:
            args.append('--armor')

        if not (HAS_SURROGATEESCAPE or armor):
            raise AnsibleError("lookup_plugin.gpg_export(%s) binary export is only supported on Python >= 3.1" % (",".join(uids)))

        export_options = kwargs.get('export_options', [])
        if len(export_options) > 0:
            args.append('--export-options')
            args.append('.'.join(export_options))

        args.extend(['--batch', '--no-tty', '--export'])

        matchmode = kwargs.get('match', 'default')
        if matchmode == 'default':
            uidformat = '{:s}'
        elif matchmode == 'exact_uid':
            uidformat = '={:s}'
        elif matchmode == 'exact_email':
            uidformat = '<{:s}>'
        elif matchmode == 'partial_email':
            uidformat = '@{:s}'
        elif matchmode == 'keygrip':
            uidformat = '&{:s}'
        else:
            raise AnsibleError("lookup_plugin.gpg_export(%s) invalid uid_match parameter %s" % (",".join(uids), matchmode))

        ret = []
        for uid in uids:
            cmd = args + [uidformat.format(uid)]

            p = subprocess.Popen(cmd,
                                 cwd=self._loader.get_basedir(),
                                 shell=False,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            (stdout, stderr) = p.communicate()

            if p.returncode != 0:
                raise AnsibleError("lookup_plugin.gpg_export(%s) returned %d" % (uid, p.returncode))
            elif len(stdout) == 0:
                raise AnsibleError("lookup_plugin.gpg_export(%s) nothing exported" % (uid))
            else:
                ret.append(to_text(stdout, errors='surrogate_or_strict'))

        return ret
