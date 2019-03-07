Ansible Role: GPG Export
========================

[![Build Status](https://travis-ci.org/znerol/ansible-role-gpg-export.svg?branch=master)](https://travis-ci.org/znerol/ansible-role-gpg-export)

Provides GPG public key lookup plugin.

Requirements
------------

[GnuPG][1] installed on controller machine.

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

Usage of `gpg_export` lookup:

    - hosts: webservers
      tasks:
        - import_role:
            name: znerol.gpg-export

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
