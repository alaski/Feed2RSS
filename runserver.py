from feed2rss import app
import sys

def main(argv=None):
    if argv is None:
        argv = sys.argv
    app.run()
    return 0

if __name__=='__main__':
    sys.exit(main())

# vim:et:ts=4:sw=4:sts=4
