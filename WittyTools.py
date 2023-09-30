#!/usr/bin/env python3
#
# WittyTools: easy tool for AkaiKKR
#    designed by Hiroki Funashima, 2023, Kindai Univ. Tech. College
#
import os
import re


class ParseConfigure(object):
    def __init__(self, inputfile='crystal.in'):
        if not os.path.isfile(inputfile):
            print('file:{} is not found.'.format(inputfile))
            exit()
        self.inputfile = inputfile
        self._set_init()
        self.main()

    def main(self):
        for line in open(self.inputfile, mode='r'):
            linebuf = self._get_linebuf(line)
            if linebuf == '':
                continue
            self._check_region(line)
            if self.region_name is None:
                pass

            elif self.region_name == 'atom_def':
                # proc for header
                if re.search(':$', linebuf):
                    continue
                self.parse_atom_definition(linebuf)

            elif self.region_name == 'atom_position':
                # proc for header
                if re.search(':$', linebuf):
                    continue
                self.parse_atom_position(linebuf)
        for x in self.atom_positions:
            print(x)
        for x in self.atom_definitions:
            print(x)

    def clear_atom_data(self):
        atom_data = {
                'atom': None,
                'x': None,
                'y': None,
                'z': None}
        return atom_data

    def check_atom_data(self, atom_data):
        check = True
        for element in ['atom', 'x', 'y', 'z']:
            if atom_data[element] is None:
                check = False
        return check

    def parse_atom_position(self, linebuf):
        data = linebuf.split(',')
        atom_data = self.clear_atom_data()
        #
        # parse atomic coordinate for x, y and z
        #
        for line in data:
            key, value = self._get_key_and_value(line)
            if key == 'atom':
                atom_data['atom'] = value
            if key == 'x':
                atom_data['x'] = value
            if key == 'y':
                if value.lower() == 'x':
                    atom_data['y'] = atom_data['x']
                else:
                    atom_data['y'] = value
            if key == 'z':
                if value.lower() == 'x':
                    atom_data['z'] = atom_data['x']
                elif value.lower() == 'y':
                    atom_data['z'] = atom_data['y']
                else:
                    atom_data['z'] = value
        if self.check_atom_data(atom_data):
            self.atom_positions.append(atom_data)
        else:
            print('** warning atomic position is incorrect.')
            print(' => {}'.format(linebuf))

    def parse_atom_definition(self, linebuf):
        if ';' not in linebuf:
            if '=' not in linebuf:
                return
            title, value = self._get_key_and_value(linebuf)
            if title == 'title' or title == 'element':
                title = value
                atom_info = []
                atom_info.append({'element':title, 'ratio': '1'})
                self.atom_definitions.append({'title':title, 'atom_info':atom_info})
            return

        header, elements = linebuf.split(';')[:2]
        #
        # for title
        #
        key, value = self._get_key_and_value(header)
        if key != 'title':
            return
        title = value
        #
        # elements
        #
        atom_info = []
        if elements == '':
            atom_info.append({'element':title, 'ratio': '1'})
            self.atom_definitions.append({'title':title, 'atom_info':atom_info})
            return
        for atom in elements.split('+'):
            element = None
            ratio = None
            #
            # check keyword, elements and ratio
            #
            for line in atom.split(','):
                key, value = self._get_key_and_value(line)
                if key == 'element':
                    element = value
                elif key == 'ratio':
                    ratio = value
            if ratio is None:
                ratio = ratio
            if element is None:
                print('** warning element is undifined.({})'.format(line))
                continue
            atom_info.append({'element': element, 'ratio': ratio})
        self.atom_definitions.append({'title':title, 'atom_info':atom_info})

    def _set_init(self):
        self.region_name = None
        self.atom_positions = []
        self.atom_definitions = []

    def _get_linebuf(self, line):
        return line.strip().split('#')[0]

    def _get_key_and_value(self, line, delimiter='='):
        key, value = [None, None]
        linebuf = self._get_linebuf(line)
        if linebuf == '':
            return [key, value]
        if delimiter not in linebuf:
            return [key, value]
        key, value = [x.strip() for x in linebuf.split(delimiter)[:2]]
        key = key.lower()
        return [key, value]

    def _check_region(self, line):
        linebuf = self._get_linebuf(line)
        if not re.search(':$', linebuf):
            return
        if linebuf == '':
            return
        linebuf = linebuf.lower()
        if re.search('^begin_', linebuf):
            self._set_region(linebuf)
        if re.search('^end_', linebuf):
            self._unset_region(linebuf)

    def _get_region_name(self, keyword, linebuf):
        data = linebuf.split(':')[0]
        prefix = '{}_'.format(keyword)
        return data.split(prefix)[1]

    def _set_region(self, linebuf):
        if self.region_name is not None:
            print('--- ParseError ---')
            print('you have already set region as {},'
                  .format(self.region_name))
            print('but your inputfile is set as {}'.format(linebuf))
            exit()
        self.region_name = self._get_region_name('begin', linebuf)

    def _unset_region(self, linebuf):
        if self.region_name is None:
            print('--- ParseError ---')
            print('you have not set region yet.')
            exit()
        clear_name = self._get_region_name('end', linebuf)
        if clear_name != self.region_name:
            print('--- ParseError ---')
            print('you have already set region as {},'
                  .format(self.region_name))
            print('but your statement is {}'.format(linebuf))
            exit()
        self.region_name = None


if __name__ == '__main__':
    ParseConfigure()
