import argparse,json
from dataclasses import asdict
from .index import ingest,search
def main():
    p=argparse.ArgumentParser();p.add_argument("--db",default="sourceground.db");sub=p.add_subparsers(dest="action",required=True)
    sub.add_parser("index").add_argument("folder");sub.add_parser("search").add_argument("query")
    a=p.parse_args()
    if a.action=="index":print("Indexed",ingest(a.db,a.folder),"chunks")
    else:print(json.dumps([asdict(x) for x in search(a.db,a.query)],indent=2))
if __name__=="__main__":main()
