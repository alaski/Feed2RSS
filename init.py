import sys
import feed2rss.scripts.initializedb as init

def main(argv=None):
    if argv is None:
        argv = sys.argv

    init.main(argv)

if __name__=='__main__':
    sys.exit(main())

# vim:et:ts=4:sw=4:sts=4
