# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from metapub.utils import asciify

# leet ipsum should not change at all (our "control").
leet_ipsum = "1F w1t t3xt r35ul7. |3tz0rz, |1nk v13w 15 aLL. T3H be b|00 kl1x r3zUltz, y0 7he 534r(h (83t4). D0 54y, 0f73n 5peNDInG iTz, != +HE p4r7I 4lvvAyz. FOr w1ll v3r510n t0. (l1(k z3aRcH w1+hOUT 1T 4nd, 47 why p1>< HELp 34513r. Up +h3 m1t3 |23p|4c3d."
leet_result = b"1F w1t t3xt r35ul7. |3tz0rz, |1nk v13w 15 aLL. T3H be b|00 kl1x r3zUltz, y0 7he 534r(h (83t4). D0 54y, 0f73n 5peNDInG iTz, != +HE p4r7I 4lvvAyz. FOr w1ll v3r510n t0. (l1(k z3aRcH w1+hOUT 1T 4nd, 47 why p1>< HELp 34513r. Up +h3 m1t3 |23p|4c3d."

# the following two samples have international alphabet characters that should get stripped out.
german_ipsum = "Rëm un Hunn duurch, dir Ierd ston dé. As déi alle séngt Friemd, fu sin hale bléit. Un fond schnéiwäiss aus. Ke wait hinnen beschéngt mir. Hun un hire zielen d'Stroos, ze get schlon klinzecht, Mecht Hämmel wee si. Léift schéinste gin de, dénen d'Mier de blo."
german_result = b"Rm un Hunn duurch, dir Ierd ston d. As di alle sngt Friemd, fu sin hale blit. Un fond schniwiss aus. Ke wait hinnen beschngt mir. Hun un hire zielen d'Stroos, ze get schlon klinzecht, Mecht Hmmel wee si. Lift schinste gin de, dnen d'Mier de blo."

volapuk_ipsum = "Ot evisitobs-li ziläk ifi. Löf nästön ospaloms sevön me."
volapuk_result = b"Ot evisitobs-li zilk ifi. Lf nstn ospaloms sevn me."

# non-ascii glyphs should get stripped out.
glyph_samples = {"¡ <-- upsidedown exclamation mark.": b" <-- upsidedown exclamation mark.",
                 "© is a copyright sign": b" is a copyright sign",
                 "® is a registered trademark": b" is a registered trademark",
                 "¾ <-- vulgar three-quarters": b" <-- vulgar three-quarters",
                 "the alpha (α) and the omega (ω)": b"the alpha () and the omega ()",
                 }


def test_glyphs():
    for glyph in list(glyph_samples.keys()):
        result = asciify(glyph)
        assert type(result) == bytes
        assert result == glyph_samples[glyph]


def test_german_ipsum():
    result = asciify(german_ipsum)
    assert type(result) == bytes
    assert result == german_result


def test_leet_ipsum():
    result = asciify(leet_ipsum)
    assert type(result) == bytes
    assert result == leet_result


def test_volapuk_ipsum():
    result = asciify(volapuk_ipsum)
    assert type(result) == bytes
    assert result == volapuk_result


if __name__=='__main__':
    test_german_ipsum()
    test_leet_ipsum()
    test_volapuk_ipsum()
