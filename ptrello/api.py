# -*- coding: utf-8 -*-

"""Main module."""
from trello import TrelloClient, List, Board, Card, Label
# import shlex
import logging
import re
import sys

from ptrello.core.config import settings
from ptrello.core.config import logger

# bs = b.get_cards(card_filter="open", filters={'fields': 'name,dueComplete,closed,url,pos,shortUrl,idMembers,idLabels,'})
# bs = b.get_cards(card_filter="open", filters={'fields':'all', 'limit':10, 'since':'2017-07-02T00:00:00.000Z'})


logger = logging.getLogger("ptrello."+__name__)


def parse_trello_objects(partial_strings):
    """
    Parse input strings to matching Trello objects
    :param partial_string: partial string to match against py-trello objects
    :return: Array of partial strings
    """
    d = {'board': None, 'list': None, 'card': None}
    s = partial_strings

    # if str(partial_strings):
    #     s = shlex.split(partial_strings)

    if len(s) is 3:
        d['board'] = s[0]
        d['list'] = s[1]
        d['card'] = s[2]
    elif len(s) is 2:
        d['board'] = s[0]
        d['list'] = s[1]
    elif len(s) is 1:
        d['card'] = s[0]
    else:
        raise ValueError("{} is an incorrect number of arguments".format(len(s)))

    logger.debug("parsed partial_string {}".format(d))

    return d


def create_trello_client(api_key=None, api_secret=None, token=None):
    """
    Creates a trello client. Uses the settings file if data is not passed.
    :param api_key: api key
    :param api_secret: api secret
    :param token: token
    :return: TrelloClient
    """
    if api_key is None:
        api_key = settings["trello_client"]["api_key"]
        api_secret = settings["trello_client"]["api_secret"]
        token = settings["trello_client"]["token"]

    return TrelloClient(api_key=api_key, api_secret=api_secret, token=token)


def get_boards(trello_client, board_filter=None, board_name=None):
    """
    Returns boards matching criteria
    :param trello_client: TrelloClient object
    :param board_name: optional board name to match
    :param board_filter: types of boards to return
    :return: 
    """
    all_boards = trello_client.list_boards(board_filter=board_filter)

    if board_name is not None:
        all_boards = [b for b in all_boards if board_name == b.name]

    logger.debug("{} boards loaded using '{}' filter".format(len(all_boards), board_filter))

    return all_boards


def get_list_from_boards(boards, list_filter=None):
    """
    Returns lists from boards
    :param boards: TrelloBoards
    :param list_filter: list filters to apply {None, open, closed}
    :return: TrelloLists
    """
    lists = [y
             for x in boards
             for y in x.list_lists(list_filter=list_filter)]

    logger.debug("{} lists returned with '{}' filter from {} boards".format(len(lists), list_filter, len(boards)))

    return lists


def get_labels_from_boards(boards):
    lbls = ([ l
                 for b in boards
                 for l in b.get_labels()])
    logger.debug("{} labels retrieved from {} boards".format(len(lbls), len(boards)))

    return lbls


def get_cards_from_boards(boards, card_filter=""):

    cards = [ c
             for b in boards
             for c in b.get_cards(card_filter=card_filter) ]

    logger.debug("{} cards retrieved with '{}' filter from {} boards".format( len(cards),card_filter \
                                                                              , len(boards) ))

    return cards


def get_list_name_for_card(card, trello_lists=None):
    if trello_lists is None:
        return card.get_list().name

    for list in trello_lists:
        if card.list_id == list.id:
            return list.name


def trello_search_cards(partial_name, trello_client=None, filters=None):
    """
    :param partial_name: 
    :param trello_client: 
    :param filters: Eg "name:Something is:open created:10 updated:2" acceptable values 
        https://developers.trello.com/v1.0/reference/#organizationsidprefsorginviterestrict
    :return: list of cards
    """
    if trello_client is None:
        trello_client = create_trello_client()


    # good way to search
    bs = trello_client.search(query="name:"+ d['card'] + " list:'In Pro' is:open created:10",partial_match=True, models=['cards'], board_ids=[b.id])
    pass


def guess_card_list_board(partial_name, trello_client=None, board_filter=None, card_filter='open', show_all_lists=False):

    if trello_client is None:
        trello_client = create_trello_client()

    d = parse_trello_objects(partial_name)

    #  Guess the board based on the what was passed.  This might not be necessary now that the argument always
    #  includese the board
    boards = guess_board(trello_client, board_filter, d)

    sorted_list = []
    for b in boards:

        # yield b

        logger.debug("Finding matching cards in '{}' board".format(b.name))

        board_lists= b.open_lists()
        board_cards = b.get_cards(card_filter=card_filter)

        if not show_all_lists:
            filtered_lists = regex_match_objects_partial_names(board_lists, d['list'])
        else:
            filtered_lists = board_lists

        filtered_cards_in_board = regex_match_objects_partial_names(board_cards, d['card'])

        #  Intersection of matched cards and lists
        filtered_card_intersect = []
        filtered_list_intersect = []

        #  Find intersections
        sorted_list.append(b)

        # if there are two arguments, assume work on only boards and lists

        for l in filtered_lists:
            card_count = 0
            if len(partial_name) > 2:
                for c in filtered_cards_in_board:
                    if l.id == c.list_id:
                        filtered_card_intersect.append(c)
                        card_count += 1
            # depending on show_all_lists flag, add to intersect
            if show_all_lists:
                filtered_list_intersect.append(l)
            elif card_count > 0:
                filtered_list_intersect.append(l)

        for l in filtered_list_intersect:
            # yield l
            sorted_list.append(l)
            if len(partial_name) > 2:
                for c in filtered_card_intersect:
                    if c.list_id == l.id:
                        # yield c
                        sorted_list.append(c)

        yield {'sorted_list':sorted_list,
               'board':b,
               'filtered_lists_intersect' : filtered_list_intersect,
               'filtered_lists' : filtered_lists,
               'filtered_cards' : filtered_card_intersect}

        logger.debug("{} cards rerturned out {} cards filtered. {} lists returned out of a possible {} "
                     "in '{}' board"\
                     .format(len(filtered_card_intersect)
                             , len(filtered_cards_in_board)
                             , len(filtered_list_intersect)
                             , len(filtered_lists)
                             , b.name))


def guess_board(trello_client, board_filter, d):

    boards = []

    if d['board'] is None and board_filter is None:
        d['board'] = settings['ptrello_settings']['default_board_id']
        boards.extend([trello_client.get_board(settings['ptrello_settings']['default_board_id'])])

    elif d['board'] is None and board_filter is not None:
        boards.extend(get_boards(trello_client, board_filter))

    elif d['board'] is not None:
        greedy_find_boards = get_boards(trello_client, board_filter)
        match_board = regex_match_objects_partial_names(greedy_find_boards, d['board'])
        boards.extend(match_board)

    else:
        error_string = "Boards could not be acquired"
        logger.error(error_string)
        raise ValueError(error_string)

    logger.debug("guessed boards: {}".format(boards))

    return boards


def regex_match_objects_partial_names(trello_object, partial_name):
    """
    Matches partial_name against objects in trell_object
    :param trello_object: Can be boards, lists, or cards, or anything with a "name" attribute
    :param partial_name: Any partial name. None values return everything
    :return: list of matching objects
    """
    if partial_name is None:
        partial_name = ""

    pattern = re.compile(partial_name, re.IGNORECASE)

    list_of_matches = []

    # Try int lookup first, the user intends on an exact match
    try:
        if int(partial_name) and type(trello_object[0]) == Card:
            logger.debug("Argument was an int value, checking cards".format())
            for o in trello_object:
                if int(o.idShort) == int(partial_name):
                    list_of_matches.append(o)
            return list_of_matches
    except:
        pass

    # Look for all objects that potentially match
    for o in trello_object:
        if pattern.search(o.name):
            list_of_matches.append(o)


    return list_of_matches


def x():
    pass


def print_trello_object(trello_object, verbose=False):

    object_type = ''

    if type(trello_object) is LookupError:
        return trello_object[0]

    if hasattr(trello_object, '__iter__'):
        r = []
        for o in trello_object:
            r.append(print_trello_object(o))

        return r

    if verbose:
        str = " {} -- {} -- {}".format(trello_object.name, trello_object.id, trello_object.desc if hasattr(trello_object, 'desc') else "")
    else:
        str = " {}".format(trello_object.name)

    if type(trello_object) is Board:
        str = "# " + (str)
        object_type = 'Board'
    elif type(trello_object) == List:
        str = "  ## {}".format(str)
        object_type = 'List'
    elif type(trello_object) == Card:
        str = "      * ({}) {}".format(trello_object.short_id, str)
        object_type = 'Card'
    elif type(trello_object) == Label:
        str = "      * ({}) {}".format(trello_object.short_id, str)
        object_type = 'Label'
    else:
        str = trello_object.name


    return (str, object_type)


def add_card(name, list, description=None, due_date=None, labels=None):

    ls = (str.split(labels))

    logger.debug("list passed: {}".format(list))

    if len(ls)>0:
        board_list = list.board
        board_labels = board_list.get_labels()

    matched_labels = []
    matched_labels.extend( convert_label_names_to_labels(ls, board_labels))

    try:
        r = list.add_card(name=name, labels=matched_labels, desc=description, due=due_date)
        logger.debug("Card added: {} ".format(r))
    except Exception as e:
        logger.warning("Card was not added, error: {}".format(e.args[0]))
        raise e

def move_card(card, target_board_id, target_list_id):
    try:
        for c in card:
            c.change_board(target_board_id)
            c.change_list(target_list_id)
            logger.debug("Card {} moved to board id {} list {} ".format(target_board_id, c, target_list_id))
    except Exception as e:
        logger.error(e)


def add_comment(card, comment):
    card.comment(comment)

def convert_label_names_to_labels(list_of_lable_names, list_of_labels):
    rids = []

    for l in list_of_labels:
        for il in list_of_lable_names:
            if str.lower(l.name) == str.lower(il):
                rids.append(l)

    return rids

def main():
    logger.debug("Main() ran.")
    client = create_trello_client()
    b = get_boards(client,'starred')
    get_list_from_boards(b, "open")
    get_labels_from_boards(b)
    get_cards_from_boards(b, "open")


if __name__ == '__main__':
    main()
