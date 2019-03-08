Ansible Role: GPG Export
========================

[![Build Status](https://travis-ci.org/znerol/ansible-role-gpg-export.svg?branch=master)](https://travis-ci.org/znerol/ansible-role-gpg-export)

Provides GPG public key lookup plugin.

Requirements
------------

[GnuPG][1] installed on controller machine.

Optional Lookup Parameters
--------------------------

* `executable`: Full path to the gpg binary. Defaults to `/usr/bin/gpg`
  (Ansible < 2.7) or located automatically in `PATH` environment variable
  (Ansible >= 2.7).
* `homedir`: Path to the gnupg home directory (see [man 1 gpg][2]). Defaults to
  GnuPG default (`~/.gnupg`).
* `armor`: Produce ASCII armored output (see [man 1 gpg][2]). Defaults to `True`.
* `export_options`: List of options for the exported keys (see [man 1 gpg][2]).
* `match`: One of `default`, `exact_uid`, `exact_email`, `partial_email`,
  specifying how keys are matched to the given uids. (see [man 1 gpg][2])


Dependencies
------------

None

Example Playbook
----------------

Usage of `gpg_export` lookup:

    - hosts: webservers
      tasks:
        - import_role:
            name: znerol.gpg_export

        - name: Publish GPG keys on webserver
          loop:
            - "Joe.Doe@Example.ORG"
            - "joe.doe@Example.com"
            - "test-wkd@example.org"
            - "me@example.com"
            - "äëöüï@example.org"
            - "foo@example.com"
          copy:
            content: "{{ lookup('gpg_export', item, armor=True, match='exact_uid') }}"
            dest: "/var/www/{{ item }}.asc"

See [test/test.yml](tests/test.yml) for sample input/output.

License
-------

MIT

[1]: https://www.gnupg.org/
[2]: https://www.gnupg.org/documentation/manpage.html
