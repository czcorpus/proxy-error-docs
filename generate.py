#!/usr/bin/env python
# Copyright (c) 2016 Charles University in Prague, Faculty of Arts,
#                    Institute of the Czech National Corpus
# Copyright (c) 2016 Tomas Machalek <tomas.machalek@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json
import os
import re
import codecs
import shutil

from jinja2 import Environment, FileSystemLoader


class Generator(object):

    def __init__(self, ident, conf):
        self._ident = ident
        self._pages = conf['pages']
        self._root_path = os.path.dirname(__file__)

    def process(self, out_dir):
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        if not os.path.isdir(os.path.join(out_dir, 'img')):
            os.makedirs(os.path.join(out_dir, 'img'))
        for page, data in self._pages.items():
            self._generate_page(page, data, out_dir)

    def _list_subdir(self, subdir_name):
        path = os.path.join(self._root_path, subdir_name, self._ident)
        return [os.path.join(path, item) for item in os.listdir(path)]

    def _load_css(self):
        ans = []
        for css in self._list_subdir('css'):
            with open(css, 'rb') as fr:
                ans.append(re.sub(r'\s+', ' ', fr.read()))
        return '\n'.join(ans)

    def _copy_images(self, target):
        for item in self._list_subdir('img'):
            shutil.copy(item, os.path.join(target, 'img'))

    def _generate_page(self, template, data, target):
        env = Environment(
            loader=FileSystemLoader(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                  'templates/%s' % self._ident))))
        tpl = env.get_template(template)
        tpl_data = dict(css=self._load_css())
        tpl_data.update(data)
        with codecs.open(os.path.join(target, template), 'wb', 'utf-8') as fw:
            fw.write(tpl.render(**tpl_data))
        self._copy_images(target)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('\nERROR: invalid arguments (use: python generate.py APP_ID)\n')
        sys.exit(1)
    app = sys.argv[1]
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'rb') as fr:
        conf = json.load(fr)
    gen = Generator(app, conf[app])
    gen.process(out_dir=os.path.join(os.path.dirname(__file__), 'dist', app))
