import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--google_token', type=str, required=False, help='Json token to access Google Docs')
parser.add_argument('--doc_data', type=str, required=False, help='Direct json payload of a google doc')
parser.add_argument('--convert', choices=['html', 'pickle'], required=True, help='What to do with the doc'
                                                                                     'Options: Convert to HTML,'
                                                                                     'Pickle into a binary')
parser.add_argument('--filename', required=True, help='filename to use for the action')


if __name__ == '__main__':
    args = parser.parse_args()
    if args.doc_data:
        pass
    elif args.google_token:
        pass
    else:
        raise KeyError('Specify either google token or doc data')

    with open(args.filename, 'wb'):
        if args.convert == 'html':
            pass
        elif args.convert == 'pickle':
            pass
