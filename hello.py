
full_size_url = 'https://cyop.mypinata.cloud/ipfs/QmU21q5oFmqGzL9Ss4nwtt3NnySGK313mSwJf16bqkYUTm/character'
image_url = 'https://cyop.mypinata.cloud/ipfs/QmTspw6bdKBREG5UCseKqVobTo27JLDuojY6BEEp1cNbDC/module'

def parse_args():
  import argparse
  import os

  parser = argparse.ArgumentParser(description='Convert Excel to JSON')
  parser.add_argument(
    '-f', '--force',
    help='Overwrite destination file if it already exists')
  parser.add_argument(
    '-o', '--outfile',
    help='Destination file (.json)')
  parser.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help='Be quiet')
  parser.add_argument(
    'src',
    nargs='+',
    type=str,
    help='source file (.xlsx)')

  return parser.parse_args()

def records_for_json(df):
  columns = [str(k) for k in df.columns]
  return [dict(zip(columns, row)) for row in df.values]

def main():
  import os
  import simplejson as json
  import pandas as pd

  class PandasJsonEncoder(json.JSONEncoder):
    def default(self, obj):
      import datetime
      if any(isinstance(obj, cls) for cls in (datetime.time, datetime.datetime, pd.Timestamp)):
        return obj.isoformat()
      elif pd.isnull(obj):
        return None
      else:
        return super(PandasJsonEncoder, self).default(obj)

  args = parse_args()

  for src in args.src:

    sheet = pd.read_excel(src, "metadata")

    columns = [str(k) for k in sheet.columns]
    columns.append('attributes')

    # items to be removed
    unwanted_key = ('CLASS', 'RARITY', 'POWER', )

    columns = [ele for ele in columns if ele not in unwanted_key]

    for index, row in sheet.iterrows():

        # Update image, fullsize url
        row['image'] = f'{image_url}{str(row["image"])}.png'
        row['fullsize'] = f'{full_size_url}{str(row["fullsize"])}.png'

        # Convert Id values to string
        row['tokenId'] = str(row['tokenId'])
        row['powerId'] = str(row['powerId'])

        # Define attributes
        nft_class = dict([('trait_type','CLASS'), ('value',row['CLASS'])])
        rarity = dict([('trait_type','RARITY'), ('value',row['RARITY'])])
        power = dict([('trait_type','POWER'), ('value',row['POWER'])])
        row['attributes'] = [nft_class, rarity, power]

        # filter row for export
        res = dict(zip(columns, row.filter(items=columns)))

        # Output files
        mode = 'w' if args.force else 'x'
        with open(f".\\files\\{res['tokenId']}.json", mode) as f:
            json.dump(res, f, ignore_nan=True, cls=PandasJsonEncoder, indent=4)

        if not args.quiet:
            arrow = '\u2192'
            print(f'{src} {arrow} {res["tokenId"]}\nJSON generated successfully!')

if __name__ == '__main__':
  main()