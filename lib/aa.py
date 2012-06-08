# aa.py
# The ASCII Art library for Python
#
# Copyright 2008-2012 Florent Gallaire <fgallaire@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import re
import textwrap
import unicodedata


def line(char, width):
    return char * width


def under(txt, char, width, over):
    ret = []
    if over:
        ret.append(line(char, lencjk(txt)))
    for lin in textwrap.wrap(txt, width):
        ret.extend([lin, line(char, lencjk(lin))])
    return ret


def box(txt, chars, width, centred=True, web=False, slides=False):
    wrap_txt = []
    char_start = ''
    if slides:
        width = width - 2
        char_start = ' '
    for lin in txt:
        wrap_txt.extend(wrap(lin, width - 4, web))
    len_cjk = max([lencjk(lin, web) for lin in wrap_txt])
    line_box = char_start + center(chars['corner'] + chars['border'] * (len_cjk + 2) + chars['corner'], width)
    line_txt = []
    for lin in wrap_txt:
        if centred:
            line_txt.append(char_start + center(chars['side'] + ' ' + center(lin, len_cjk, web) + ' ' + chars['side'], width, web))
        else:
            line_txt.append(char_start + center(chars['side'] + ' ' + lin + ' ' * (len_cjk - lencjk(lin, web) + 1) + chars['side'], width, web))
    return [line_box] + line_txt + [line_box]


def header(header_data, chars, width, height, web, slides):
    h = [header_data[v] for v in header_data if v.startswith("HEADER") and header_data[v]]
    n_h = len(h)
    height_box = sum([len(box([header], chars, width, slides=slides)) for header in h])
    if not n_h:
        return []
    if not slides:
        n, end = 2, 0
    else:
        x = height - 3 - height_box
        n = x / (n_h + 1)
        end = x % (n_h + 1)
    header = [line(chars['bar2'], width)]
    header.extend([''] * n)
    for h in 'HEADER1', 'HEADER2', 'HEADER3':
        if header_data[h]:
            header.extend(box([header_data[h]], chars, width, slides=slides))
            header.extend([''] * n)
    header.extend([''] * end)
    header.append(line(chars['bar2'], width))
    if web and slides:
        header = ['<section><pre>' + header[0]] + header[1:-1] + [header[-1] + '</pre></section>']
    if not slides:
        header = [''] + header
    return header


def slide(title, char, width, web):
    res = [line(char, width)]
    res.append('')
    res.append(center(title, width)[:width])
    res.append('')
    res.append(line(char, width))
    if web:
        res = ['<section><pre>' + res[0]] + res[1:]
    return res


def table(data, chars, width, border, h_header, v_header, align, spread, web):
    n = max([len(lin[0]) for lin in data])
    data3 = []
    for lin in data:
        if  max(lin[1]) == 1:
            data3.append(lin[0])
        else:
            newline = []
            for i, el in enumerate(lin[0]):
                if lin[1][i] == 1:
                    newline.append(el)
                else:
                    newline.extend(lin[1][i] * [''])
            data3.append(newline)
    tab = []
    for i in range(n):
        tab.append([lin[i] for lin in data3])
    if web:
        length = [max([lencjk(re.sub('<a.*">|</a>', '', el)) for el in lin]) for lin in tab]
    else:
        length = [max([lencjk(el) for el in lin]) for lin in tab]
    if spread:
        data[0][0] = [data[0][0][i].center(length[i]) for i in range(n)]
    bord, side, corner, vhead = chars['border'], chars['side'], chars['corner'], chars['vhead']
    if border:
        hhead = chars['hhead']
    else:
        hhead = chars['border']
    resh = res = corner
    for i in range(n):
        res = res + (length[i] + 2) * bord + corner
        resh = resh + (length[i] + 2) * hhead + corner
    ret = []
    for i, lin in enumerate(data):
        aff = side
        if i == 1 and h_header:
            ret.append(resh)
        else:
            if i == 0 or border:
                ret.append(res)
        for j, el in enumerate(lin[0]):
            if web:
                aff = aff + " " + el + (sum(length[j:(j + lin[1][j])]) + lin[1][j] * 3 - lencjk(re.sub('<a.*">|</a>', '',el)) - 2) * " " + side
            else:
                aff = aff + " " + el + (sum(length[j:(j + lin[1][j])]) + lin[1][j] * 3 - lencjk(el) - 2) * " " + side
            if j == 0 and v_header:
                aff = aff[:-1] + vhead
        ret.append(aff)
    ret.append(res)
    if align == 'Left':
        ret = [' ' * 2  + lin for lin in ret]
    elif align == 'Center' and not (web and spread):
        ret = [center(lin, width) for lin in ret]
    return ret


def image(image):
    art_table = '#$!;:,. '
    art_image = []
    for lin in image:
        art_line = ''
        for pixel in lin:
            art_line = art_line + art_table[pixel/32]
        art_image.append(art_line)
    return art_image


def wrap(txt, width, web):
    if not web:
        return textwrap.wrap(txt, width)
    txt = re.split('(<a href=.*?>)|(</a>)|(<img src=.*?>)', txt)
    lin, length, ret = '', 0, []
    for el in txt:
        if el:
            if el[0] != '<':
                if len(el) > width:
                    lin = lin + el
                    multi = textwrap.wrap(lin, width)
                    ret.extend(multi[:-1])
                    lin = multi[-1]
                elif length + len(el) <= width:
                    length = length + len(el)
                    lin = lin + el
                else:
                    ret.append(lin)
                    lin, length = el, len(el)
            else:
                    lin = lin + el
    ret.append(lin)
    return ret


def lencjk(txt, web=False):
    if web:
        txt = re.sub('(<a href=.*?>)|(</a>)|(<img src=.*?>)', '', txt)
    if isinstance(txt, str):
        return len(txt)
    l = 0
    for char in txt:
        if unicodedata.east_asian_width(unicode(char)) in ('F', 'W'):
            l = l + 2
        else:
            l = l + 1
    return l


def center(txt, width, web=False):
    n_before = (width - lencjk(txt, web)) / 2
    n_after = width - lencjk(txt, web) - n_before
    return ' ' * n_before + txt + ' ' * n_after
