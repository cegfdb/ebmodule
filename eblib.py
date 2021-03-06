# eblib.py
# Tamito KAJIYAMA <13 September 2001>
# $Id: eblib.py,v 1.2 2001/09/22 23:44:08 kajiyama Exp $

from eb import *

import string

class EB_Hit:
    def __init__(self, book, subbook, position):
        self.book = book # EB instance
        self.subbook = subbook
        self.position = position # (heading, text)
    def heading(self, container=None):
        return self.book.get_content(
            self.subbook, self.position[0], container, eb_read_heading)
    def text(self, container=None):
        return self.book.get_content(
            self.subbook, self.position[1], container, eb_read_text)

class EB:
    def __init__(self, dir):
        self.book     = EB_Book()
        self.appendix = EB_Appendix()
        self.hookset  = EB_Hookset()
        eb_set_hooks(self.hookset, (
            (EB_HOOK_NEWLINE,              self.handle_newline),
            (EB_HOOK_SET_INDENT,           self.handle_set_indent),
            (EB_HOOK_NARROW_FONT,          self.handle_font),
            (EB_HOOK_WIDE_FONT,            self.handle_font),
            (EB_HOOK_STOP_CODE,            self.handle_stop_code),
            (EB_HOOK_BEGIN_NARROW,         self.handle_tags),
            (EB_HOOK_END_NARROW,           self.handle_tags),
            (EB_HOOK_BEGIN_SUBSCRIPT,      self.handle_tags),
            (EB_HOOK_END_SUBSCRIPT,        self.handle_tags),
            (EB_HOOK_BEGIN_SUPERSCRIPT,    self.handle_tags),
            (EB_HOOK_END_SUPERSCRIPT,      self.handle_tags),
            (EB_HOOK_BEGIN_NO_NEWLINE,     self.handle_tags),
            (EB_HOOK_END_NO_NEWLINE,       self.handle_tags),
            (EB_HOOK_BEGIN_EMPHASIS,       self.handle_tags),
            (EB_HOOK_END_EMPHASIS,         self.handle_tags),
            (EB_HOOK_BEGIN_CANDIDATE,      self.handle_tags),
            (EB_HOOK_END_CANDIDATE_GROUP,  self.handle_tags),
            (EB_HOOK_END_CANDIDATE_LEAF,   self.handle_tags),
            (EB_HOOK_BEGIN_REFERENCE,      self.handle_tags),
            (EB_HOOK_END_REFERENCE,        self.handle_tags),
            (EB_HOOK_BEGIN_KEYWORD,        self.handle_tags),
            (EB_HOOK_END_KEYWORD,          self.handle_tags),
            (EB_HOOK_BEGIN_MONO_GRAPHIC,   self.handle_tags),
            (EB_HOOK_END_MONO_GRAPHIC,     self.handle_tags),
            (EB_HOOK_BEGIN_GRAY_GRAPHIC,   self.handle_tags),
            (EB_HOOK_END_GRAY_GRAPHIC,     self.handle_tags),
            (EB_HOOK_BEGIN_COLOR_BMP,      self.handle_tags),
            (EB_HOOK_BEGIN_COLOR_JPEG,     self.handle_tags),
            (EB_HOOK_END_COLOR_GRAPHIC,    self.handle_tags),
            (EB_HOOK_BEGIN_IN_COLOR_BMP,   self.handle_tags),
            (EB_HOOK_BEGIN_IN_COLOR_JPEG,  self.handle_tags),
            (EB_HOOK_END_IN_COLOR_GRAPHIC, self.handle_tags),
            (EB_HOOK_BEGIN_WAVE,           self.handle_tags),
            (EB_HOOK_END_WAVE,             self.handle_tags),
            (EB_HOOK_BEGIN_MPEG,           self.handle_tags),
            (EB_HOOK_END_MPEG,             self.handle_tags)))
        self.bind(dir)
        self.set_subbook(0)
    def handle_newline(self, book, appendix, container, code, argv):
        ##print "handle_newline: code=%d, argv=%s" % (code, repr(argv))
        self.hook_newline(container)
        return EB_SUCCESS
    def handle_set_indent(self, book, appendix, container, code, argv):
        ##print "handle_set_indent: code=%d, argv=%s" % (code, repr(argv))
        self.hook_set_indent(container, argv[1])
        return EB_SUCCESS
    def handle_font(self, book, appendix, container, code, argv):
        ##print "handle_font: code=%d, argv=%s" % (code, repr(argv))
        if code == EB_HOOK_NARROW_FONT:
            self.hook_narrow_font(container, argv[0])
        elif code == EB_HOOK_WIDE_FONT:
            self.hook_wide_font(container, argv[0])
        return EB_SUCCESS
    def handle_tags(self, book, appendix, container, code, argv):
        ##print "handle_tags: code=%d, argv=%s" % (code, repr(argv))
        if code == EB_HOOK_BEGIN_NARROW:
            self.hook_begin_narrow(container)
        elif code == EB_HOOK_END_NARROW:
            self.hook_end_narrow(container)
        elif code == EB_HOOK_BEGIN_SUBSCRIPT:
            self.hook_begin_subscript(container)
        elif code == EB_HOOK_END_SUBSCRIPT:
            self.hook_end_subscript(container)
        elif code == EB_HOOK_BEGIN_SUPERSCRIPT:
            self.hook_begin_superscript(container)
        elif code == EB_HOOK_END_SUPERSCRIPT:
            self.hook_end_superscript(container)
        elif code == EB_HOOK_BEGIN_NO_NEWLINE:
            self.hook_begin_no_newline(container)
        elif code == EB_HOOK_END_NO_NEWLINE:
            self.hook_end_no_newline(container)
        elif code == EB_HOOK_BEGIN_EMPHASIS:
            self.hook_begin_emphasis(container)
        elif code == EB_HOOK_END_EMPHASIS:
            self.hook_end_emphasis(container)
        elif code == EB_HOOK_BEGIN_REFERENCE:
            self.hook_begin_reference(container)
        elif code == EB_HOOK_END_REFERENCE:
            self.hook_end_reference(container, argv[1], argv[2])
        elif code == EB_HOOK_BEGIN_KEYWORD:
            self.hook_begin_keyword(container)
        elif code == EB_HOOK_END_KEYWORD:
            self.hook_end_keyword(container)
        return EB_SUCCESS
    def handle_stop_code(self, book, appendix, container, code, argv):
        ##print "handle_stop_code: code=%d, argv=%s" % (code, repr(argv))
        return eb_hook_stop_code(book, appendix, container, code, argv)
    def write_text(self, text):
        eb_write_text(self.book, text)
    def get_content(self, subbook, position, container, func):
        # save current subbook
        current_subbook = self.subbook()
        if current_subbook != subbook:
            self.set_subbook(subbook)
        else:
            current_subbook = None
        # get content at the specified subbook/position
        eb_seek_text(self.book, position)
        buffer = []
        while 1:
            data = func(self.book, self.appendix, self.hookset, container)
            if not data:
                break
            buffer.append(data)
        # restore current subbook
        if current_subbook is not None:
            self.set_subbook(current_subbook)
        return string.join(buffer, '')
    # callbacks
    def hook_newline(self, container):
        self.write_text("\n")
    def hook_set_indent(self, container, indent):
        pass
    def hook_narrow_font(self, container, code):
        try:
            text = eb_narrow_alt_character_text(self.appendix, code)
        except EBError:
            text = "?"
        self.write_text(text)
    def hook_wide_font(self, container, code):
        try:
            text = eb_wide_alt_character_text(self.appendix, code)
        except EBError:
            text = "?"
        self.write_text(text)
    def hook_begin_narrow(self, container):
        pass
    def hook_end_narrow(self, container):
        pass
    def hook_begin_subscript(self, container):
        pass
    def hook_end_subscript(self, container):
        pass
    def hook_begin_superscript(self, container):
        pass
    def hook_end_superscript(self, container):
        pass
    def hook_begin_no_newline(self, container):
        pass
    def hook_end_no_newline(self, container):
        pass
    def hook_begin_emphasis(self, container):
        pass
    def hook_end_emphasis(self, container):
        pass
    def hook_begin_reference(self, container):
        pass
    def hook_end_reference(self, container, page, offset):
        pass
    def hook_begin_keyword(self, container):
        pass
    def hook_end_keyword(self, container):
        pass
    # functions
    def bind(self, dir):
        eb_bind(self.book, dir)
    def suspend(self):
        eb_suspend(self.book)
    def is_bound(self):
        return eb_is_bound(self.book)
    def path(self):
        return eb_path(self.book)
    def character_code(self):
        return eb_character_code(self.book)
    def disc_type(self):
        return eb_disc_type(self.book)
    def load_all_subbooks(self):
        eb_load_all_subbooks(self.book)
    def subbook_list(self):
        return eb_subbook_list(self.book)
    def set_subbook(self, subbook):
        eb_set_subbook(self.book, subbook)
    def unset_subbook(self):
        eb_unset_subbook(self.book)
    def subbook(self):
        return eb_subbook(self.book)
    def subbook_title(self, subbook=None):
        if subbook is None:
            return eb_subbook_title(self.book)
        return eb_subbook_title2(self.book, subbook)
    def subbook_directory(self, subbook=None):
        if subbook is None:
            return eb_subbook_directory(self.book)
        return eb_subbook_directory2(self.book, subbook)
    def copyright(self):
        if eb_have_copyright(self.book):
            return EB_Hit(self, None, eb_copyright(self.book))
        return None
    def menu(self):
        if eb_have_menu(self.book):
            return EB_Hit(self, None, eb_menu(self.book))
        return None
    def search_exactword(self, word):
        return self.do_search(eb_search_exactword, word)
    def search_word(self, word):
        return self.do_search(eb_search_word, word)
    def search_endword(self, word):
        return self.do_search(eb_search_endword, word)
    def do_search(self, func, word):
        func(self.book, word)
        buffer = []
        while 1:
            hitlist = eb_hit_list(self.book)
            if not hitlist:
                break
            subbook = self.subbook()
            for hit in hitlist:
                buffer.append(EB_Hit(self, subbook, hit))
        return buffer

def test():
    import sys
    argc = len(sys.argv)
    if argc != 2 and argc != 4:
        sys.stderr.write("Usage: python eblib.py dir [subbook] [word]\n")
        sys.exit(1)

    class EBTest(EB):
        def hook_narrow_font(self, container, code):
            self.write_text("<gaiji=h%04x>" % code)
        def hook_wide_font(self, container, code):
            self.write_text("<gaiji=z%04x>" % code)
        def hook_begin_reference(self, container):
            self.write_text("<reference>")
        def hook_end_reference(self, container, page, offset):
            self.write_text("</reference=%x:%x>" % (page, offset))
        def hook_begin_keyword(self, container):
            self.write_text("<keyword>")
        def hook_end_keyword(self, container):
            self.write_text("</keyword>")

    eb_initialize_library()
    eb = EBTest(sys.argv[1])
    if argc == 2:
        for subbook in eb.subbook_list():
            print "#%d. %s (%s)" % (subbook,
                                    eb.subbook_title(subbook),
                                    eb.subbook_directory(subbook))
    else:
        eb.set_subbook(int(sys.argv[2]))
        word = sys.argv[3]
        if word[-1:] == "*":
            func = eb.search_word
            word = word[:-1]
        elif word[:1] == "*":
            func = eb.search_endword
            word = word[1:]
        else:
            func = eb.search_exactword
        for hit in func(word):
            print "-" * 40
            print hit.heading()
            print hit.text()
    eb_finalize_library()

if __name__ == "__main__":
    test()
