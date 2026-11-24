"""
OMML (Office Math Markup Language) -> LaTeX 转换器
覆盖考研公式表常见结构: 分数/上下标/根号/求和积分/括号/函数/重音/矩阵
"""
from lxml import etree

M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def q(tag, ns=M_NS):
    return f'{{{ns}}}{tag}'


NARY_CHR = {
    '∫': r'\int', '∬': r'\iint', '∭': r'\iiint', '∮': r'\oint',
    '∑': r'\sum', '∏': r'\prod', '⋃': r'\bigcup', '⋂': r'\bigcap',
    '∐': r'\coprod', '∫∫': r'\iint',
}

ACC_CHR = {
    '\u0302': r'\hat', '\u0303': r'\tilde', '\u20d7': r'\vec',
    '\u0304': r'\bar', '\u0305': r'\overline', '\u0307': r'\dot',
    '\u0308': r'\ddot', '\u030c': r'\check', '\u0301': r'\acute',
}

DELIM_MAP = {
    '(': '(', ')': ')', '[': '[', ']': ']', '{': r'\{', '}': r'\}',
    '|': '|', '‖': r'\|', '⟨': r'\langle', '⟩': r'\rangle',
    '': '.', '\uE0B0': '.',
}


def _chr(el, tag, default=''):
    if el is None:
        return default
    pr = el.find(q(tag))
    if pr is None:
        return default
    c = pr.find(q('chr'))
    if c is None:
        return default
    return c.get(q('val'), default)


def _val(el, tag, default=None):
    if el is None:
        return default
    pr = el.find(q(tag))
    if pr is None:
        return default
    v = pr.get(q('val'))
    return v if v is not None else default


def conv(el):
    """把一个 OMML 节点转成 LaTeX 字符串"""
    if el is None:
        return ''
    tag = etree.QName(el).localname if el.tag.startswith('{') else el.tag

    if tag in ('oMath', 'oMathPara', 'e', 'num', 'den', 'sub', 'sup', 'fName', 'lim', 'deg'):
        return ''.join(conv(c) for c in el)

    if tag == 'r':
        return _conv_run(el)

    if tag == 't':
        return el.text or ''

    if tag == 'f':
        num = _child(el, 'num')
        den = _child(el, 'den')
        return r'\frac{' + conv(num) + '}{' + conv(den) + '}'

    if tag == 'sSup':
        return '{' + conv(_child(el, 'e')) + '}^{' + conv(_child(el, 'sup')) + '}'

    if tag == 'sSub':
        return '{' + conv(_child(el, 'e')) + '}_{' + conv(_child(el, 'sub')) + '}'

    if tag == 'sSubSup':
        return '{' + conv(_child(el, 'e')) + '}_{' + conv(_child(el, 'sub')) + '}^{' + conv(_child(el, 'sup')) + '}'

    if tag == 'sPre':
        return '{}_{' + conv(_child(el, 'sub')) + '}^{' + conv(_child(el, 'sup')) + '}' + conv(_child(el, 'e'))

    if tag == 'rad':
        deg = _child(el, 'deg')
        e = _child(el, 'e')
        hide = _val(el, 'radPr') or ''
        d = conv(deg).strip()
        if d and d not in ('', '2'):
            return r'\sqrt[' + d + ']{' + conv(e) + '}'
        return r'\sqrt{' + conv(e) + '}'

    if tag == 'nary':
        chr_ = _chr(el, 'naryPr', '∫')
        op = NARY_CHR.get(chr_, r'\int')
        sub = conv(_child(el, 'sub')).strip()
        sup = conv(_child(el, 'sup')).strip()
        e = conv(_child(el, 'e'))
        s = op
        if sub:
            s += '_{' + sub + '}'
        if sup:
            s += '^{' + sup + '}'
        return s + ' ' + e

    if tag == 'd':
        beg = DELIM_MAP.get(_chr(el, 'dPr', '('), _chr(el, 'dPr', '('))
        end = DELIM_MAP.get(_chr(el, 'dPr', ')'), _chr(el, 'dPr', ')'))
        parts = [conv(c) for c in el.findall(q('e'))]
        sep = _chr(el, 'dPr', '|')
        inner = (r'\middle' + sep).join(parts) if len(parts) > 1 else (parts[0] if parts else '')
        return r'\left' + beg + ' ' + inner + r' \right' + end

    if tag == 'func':
        fn = conv(_child(el, 'fName')).strip()
        e = conv(_child(el, 'e'))
        if fn:
            return fn + r'\left(' + e + r'\right)'
        return e

    if tag == 'acc':
        c = _chr(el, 'accPr', '\u0302')
        op = ACC_CHR.get(c, r'\hat')
        return op + '{' + conv(_child(el, 'e')) + '}'

    if tag == 'bar':
        pos = _val(el, 'barPr', 'top')
        op = r'\overline' if pos != 'bot' else r'\underline'
        return op + '{' + conv(_child(el, 'e')) + '}'

    if tag == 'limLow':
        return r'\underset{' + conv(_child(el, 'lim')) + '}{' + conv(_child(el, 'e')) + '}'

    if tag == 'limUpp':
        return r'\overset{' + conv(_child(el, 'lim')) + '}{' + conv(_child(el, 'e')) + '}'

    if tag == 'groupChr':
        return conv(_child(el, 'e'))

    if tag == 'eqArr':
        rows = [conv(c) for c in el.findall(q('e'))]
        return r'\begin{aligned}' + r'\\'.join(rows) + r'\end{aligned}'

    if tag == 'm':
        rows = []
        for mr in el.findall(q('mr')):
            rows.append(' & '.join(conv(c) for c in mr.findall(q('e'))))
        return r'\begin{matrix}' + r'\\'.join(rows) + r'\end{matrix}'

    if tag in ('box', 'borderBox', 'phant'):
        return conv(_child(el, 'e'))

    if tag in ('ctrlPr', 'rPr', 'fPr', 'naryPr', 'dPr', 'radPr', 'accPr', 'barPr', 'sSupPr', 'sSubPr', 'sSubSupPr',
               'funcPr', 'limLowPr', 'limUppPr', 'groupChrPr', 'mPr', 'eqArrPr', 'mrPr'):
        return ''

    # 默认: 递归子节点
    return ''.join(conv(c) for c in el)


def _child(el, tag):
    if el is None:
        return None
    return el.find(q(tag))


def _conv_run(r):
    """处理 m:r, 转义原本是文本但含 LaTeX 特殊字符的内容"""
    txt = ''.join(t.text or '' for t in r.findall(q('t')))
    if not txt:
        return ''
    # 文本里的特殊字符需要转义 (但数学 run 里通常是纯符号, 只处理少量)
    out = []
    for ch in txt:
        if ch in '\\':
            out.append(r'\backslash ')
        elif ch == '&':
            out.append(r'\&')
        elif ch == '%':
            out.append(r'\%')
        elif ch == '#':
            out.append(r'\#')
        elif ch == '_':
            out.append(r'\_')
        elif ch == '^':
            out.append(r'\hat{}')
        else:
            out.append(ch)
    return ''.join(out)


def omml_to_latex(omath_el):
    """输入 m:oMath 元素, 输出 LaTeX"""
    return conv(omath_el).strip()


def cell_to_mixed(cell_el):
    """
    把 w:tc 单元格转为 '文本 + $latex$' 混合串
    遍历单元格所有子元素, 文本保留, 公式用 $...$ 包裹
    """
    pieces = []
    for node in cell_el.iter():
        ln = etree.QName(node).localname
        if ln == 'oMath':
            latex = omml_to_latex(node)
            if latex:
                pieces.append('$' + latex + '$')
        elif ln == 't':
            # 跳过 oMath 内部的 t (已经处理过)
            anc = node.getparent()
            in_math = False
            while anc is not None:
                if etree.QName(anc).localname in ('oMath', 'oMathPara'):
                    in_math = True
                    break
                anc = anc.getparent()
            if not in_math and node.text:
                pieces.append(node.text)
        elif ln == 'br':
            pieces.append('\n')
    return ''.join(pieces).strip()
