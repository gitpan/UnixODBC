use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

# $Id: Makefile.PL,v 1.2 2003/07/13 01:39:34 kiesling Exp $

WriteMakefile(
    'NAME'		=> 'UnixODBC',
    'VERSION_FROM'      => 'UnixODBC.pm',
    'LIBS'		=> ['-L/usr/local/lib -L/usr/lib -lodbc'],
);




