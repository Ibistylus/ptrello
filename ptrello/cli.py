# -*- coding: utf-8 -*-

"""Console script for ptrello."""
import sys
import click
import logging
from ptrello import api
from ptrello.core.config import logger

# from ptrello.core.config import settings
# import inspect

logger = logging.getLogger("ptrello."+__name__)
default_note = "quicknote.txt"

class Config(object):
    l = []
    pass


#  pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(chain=True)
#  @pass_config
@click.pass_context
def main(ctx):
    ctx.obj ={'trello':None}
    pass


@click.pass_context
def populate_context(ctx, args, show_all_lists, board_filter, card_filter, target_list=None):
    input_text = args
    _output = []
    _target = []
    ctx.obj['input_args'] = args

    try:
        if not ctx.obj['trello']:
            ctx.obj['input_args'] = args

            e = api.guess_card_list_board(input_text, board_filter=board_filter, card_filter=card_filter,
                                      show_all_lists=show_all_lists)

            _output.extend(e)

            ctx.obj['trello'] = _output

        if target_list:
            ctx.obj['input_args_target_list'] = target_list
            _target = []
            _target.extend( api.guess_card_list_board(target_list, board_filter=board_filter
                                                          , card_filter=card_filter, show_all_lists=False))

            ctx.obj['target_ctx'] = _target

    except ValueError as err:
        handle_error(err)
        logger.warning("Could not retrieve trello objects. {}".format(err))

@main.command('card')
@click.pass_context
@click.argument('args', nargs=3, required=False)
@click.option('--match_all_lists/--match_intersect_lists', default=False, help='Show all lists, or only those that match')
@click.option('--card_filter', default='open', help='Card filter (open, closed)')
@click.option('--board_filter', default='starred', help='Board filter (starred, open, close)')
def card(ctx, args, match_all_lists, board_filter, card_filter):

    try:
        if not ctx.obj['trello']:
            populate_context(args,board_filter=board_filter, card_filter=card_filter, show_all_lists=match_all_lists)

        print_context_sorted_list()


    except ValueError as err:
        handle_error(err)
    pass


@main.command()
@click.pass_context
@click.argument('args', nargs=3, required=False)
@click.option('--match_all_lists/--match_intersect_lists', default=False, help='Show all lists, or only those that match')
@click.option('--card_filter', default='open', help='Card filter (open, closed)')
@click.option('--board_filter', default='starred', help='Board filter (starred, open, close)')
def show(ctx, args, match_all_lists, board_filter, card_filter):
    try:
        if not ctx.obj['trello']:
            populate_context(args,board_filter=board_filter, card_filter=card_filter, show_all_lists=match_all_lists)
    except:
        pass

    try:
        print_context_card_detail()

    except Exception as e:
        logger.error("Handled error occured: {}".format(e.args[0]))
        click.secho(e.args[0], fg='red')


@main.command()
@click.pass_context
@click.argument('args', nargs=3, required=False)
@click.option('--match_all_lists/--match_intersect_lists', default=False, help='Show all lists, or only those that match')
@click.option('--card_filter', default='open', help='Card filter (open, closed)')
@click.option('--board_filter', default='starred', help='Board filter (starred, open, close)')
def add(ctx, args, match_all_lists, board_filter, card_filter):

    try:
        if not ctx.obj['trello']:
            populate_context(args,board_filter=board_filter, card_filter=card_filter, show_all_lists=match_all_lists)
    except:
        pass

    cards = get_context_filtered_cards()
    list = get_context_filtered_lists()

    if len(cards) or len(list) > 1:
        error_string = "There were {} lists and {} cards matching.Please make the card name is unique " \
                       "and there is only one list to place the card on.".format(len(list), len(cards))

        click.secho(error_string, fg='red')

        return


    description = click.prompt('Enter a description', default='')
    labels = click.prompt('Enter labels seperated by spaces', default='personal', show_default=True)
    due_date = click.prompt('Enter due date', show_default=True, default='')

    print(ctx.obj['input_args'][-1])
    print(ctx.obj['trello'][0]['filtered_lists'][0])
    api.add_card(list=ctx.obj['trello'][0]['filtered_lists'][0], name=ctx.obj['input_args'][-1], description= description,
                     labels=labels, due_date=due_date)





@main.command()
@click.pass_context
@click.argument('args', nargs=3, required=False)
@click.option('--text',default=None, required=False)
@click.option('--match_all_lists/--match_intersect_lists', default=False, help='Show all lists, or only those that match')
@click.option('--card_filter', default='open', help='Card filter (open, closed)')
@click.option('--board_filter', default='starred', help='Board filter (starred, open, close)')
def comment(ctx, args, text, match_all_lists, board_filter, card_filter):

    try:
        if not ctx.obj['trello']:
            populate_context(args,board_filter=board_filter, card_filter=card_filter, show_all_lists=match_all_lists)
    except:
        pass

    cards = get_context_filtered_cards()

    if len(cards) > 1:
        error_string = "More than one card found--(). Could not add comments".format( len(cards))

        click.secho(error_string, fg='red')

        return

    if not text:
        text = click.prompt('Enter comment', show_default=True, default='')

    api.add_comment(cards[0], text)



@main.command()
@click.pass_context
@click.argument('args', nargs=3, required=False)
@click.option('--target_list', nargs=2, required=True)
@click.option('--match_all_lists/--match_intersect_lists', default=False, help='Show all lists, or only those that match')
@click.option('--card_filter', default='open', help='Card filter (open, closed)')
@click.option('--board_filter', default='starred', help='Board filter (starred, open, close)')
def move(ctx, args, target_list, match_all_lists, board_filter, card_filter):

    try:
        if not args and ctx.obj['input_args']:
            args = ctx.obj['input_args']
            print(args)
        else:
            pass

        populate_context(args, board_filter=board_filter, card_filter=card_filter
                                                 , show_all_lists=match_all_lists, target_list=target_list)

        c = get_context_filtered_cards()

        if len(c) > 0:
            yn = click.prompt("There are {} cards selected, are you sure you want to move them all?".format(len(c)))
            if yn.lower() == 'y':
                target_board = ctx.obj['target_ctx'][0]['board']
                api.move_card(card=c, target_board_id=target_board.id, target_list_id=ctx.obj['target_ctx'][0]['filtered_lists'][0].id)


            else:
                click.secho("card(s) not moved")
                return

    except Exception as e:
        handle_error(e, sys._getframe().f_code.co_name)



@click.pass_context
def get_context_sorted_list(ctx):
    for obj in ctx.obj['trello']:
        return obj['sorted_list']


@click.pass_context
def get_context_filtered_cards(ctx):
    for obj in ctx.obj['trello']:
        # print(obj['filtered_cards'])
        return obj['filtered_cards']


@click.pass_context
def get_context_filtered_lists(ctx):
    for obj in ctx.obj['trello']:
        return obj['filtered_lists']


def print_context_sorted_list():
    try:
        for item in get_context_sorted_list():
            click.secho(api.print_trello_object(item)[0], fg='yellow')
    except Exception as e:
        pass


def print_context_cards():
        for item in get_context_filtered_cards():
            click.secho(api.print_trello_object(item)[0], fg='yellow')


def print_context_lists():
        for item in get_context_filtered_lists():
            click.secho(api.print_trello_object(item)[0], fg='yellow')


def get_context_card_detail(get_comments=False):

    list_of_card_dicts = []

    for item in get_context_filtered_cards():
        comments = []

        card_dict = {}

        if get_comments:
            comments.extend(reversed(item.get_comments()))

        card_dict['short_id'] = item.short_id
        card_dict['name'] = item.name
        card_dict['board_name'] = item.board.name
        card_dict['list_name'] = api.get_list_name_for_card(item ,get_context_filtered_lists())
        card_dict['card_created_date'] = item.card_created_date
        card_dict['due_date'] = item.due_date
        card_dict['description'] = item.description
        card_dict['labels'] = item.labels
        card_dict['comments'] = comments

        list_of_card_dicts.append(card_dict)

    return list_of_card_dicts


def print_context_card_detail():
    loc = get_context_card_detail(True)

    for item in loc:
        click.secho(100 * "-", fg='blue')
        click.secho("\n", fg='blue')
        click.secho(u"### Name({}): {}".format(item['short_id'], item['name']), fg='green', bold=True, nl="\n")
        click.secho(u"Path: {} > {}".format(item['board_name'],item['list_name']), fg='yellow', nl="\n\n")
        click.secho(u"Create Date: {} ".format(item['card_created_date']), fg='yellow', nl="\n")
        click.secho(u"Due Date: {} ".format(item['due_date']), fg='yellow', nl="\n")
        click.secho(u"Desc: {} ".format(item['description']), fg='yellow', nl="\n")
        click.secho(u"Labels: {} ".format(item['labels']), fg='yellow', nl="\n")
        click.secho(u"Comments: ", fg='yellow')
        for comm in item['comments']:
            click.secho(u"{} - {} ".format(comm['date'], comm['data']['text']), fg='yellow', nl="\n")
        click.secho("\n")


def handle_error(err, name=None):
    ep = ""

    for e in err.args:
        ep += e
    click.secho(e, fg='red')
    logger.warning("{} type error encountered from function {}: {} ".format(type(err), name, err))

if __name__ == "__main__":
    main(obj={'trello':None})
