# $Id: Makefile.PL,v 1.2 2003/07/14 13:43:08 kiesling Exp $

my $makefile = <<EOMAKEFILE;
all: install

install: 
	perl installscripts

clean:
	rm -f Makefile Makefile.old

test:
	sh -c true
EOMAKEFILE

print "Creating Makefile in bridge/.\n";
open OUT, ">Makefile" or die "Couldn't create Makefile: $!\n";
print OUT $makefile;
close OUT;
