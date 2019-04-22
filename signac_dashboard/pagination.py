# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from math import ceil


class Pagination(object):
    """Pagination adapted from http://flask.pocoo.org/snippets/44/

    :param int page: Current page number.
    :param int per_page: Number of items per page. If 0 or `None`, all items
                         will be displayed on one page.
    :param int total_count: The total number of items being paginated.
    """

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        if self.per_page is None or self.per_page == 0:
            return 1
        else:
            return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def first_item(self):
        if self.per_page is None:
            return 0
        else:
            return max((self.page - 1) * self.per_page, 0)

    def last_item(self):
        if self.per_page is None:
            return self.total_count
        else:
            return min(self.page * self.per_page, self.total_count)

    def paginate(self, items):
        if items is None:
            return []
        else:
            return items[self.first_item():self.last_item()]

    def item_counts(self, tag='jobs'):
        if self.total_count > 0:
            return '{} to {} of {} {}'.format(
                    self.first_item() + 1, self.last_item(),
                    self.total_count, tag)
        else:
            return '{} {}'.format(self.total_count, tag)

    def iter_pages(self, left_edge=2, left_current=3,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
