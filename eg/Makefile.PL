# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

# $Id: Makefile.PL,v 1.5 2003/07/14 02:39:13 kiesling Exp $

my $makefile = <<EOMAKEFILE;
all: install

install: 
	perl installscripts

clean:
	rm -f Makefile Makefile.old

test:
	sh -c true
EOMAKEFILE

print "Creating Makefile in eg/.\n";
open OUT, ">Makefile" or die "Couldn't create Makefile: $!\n";
print OUT $makefile;
close OUT;
